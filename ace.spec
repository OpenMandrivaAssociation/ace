%define lib_major       5
%define lib_name        %mklibname %{name} %{lib_major}
%define lib_name_devel  %mklibname %{name} -d

Name: ace
Version: 5.6
Release: %mkrel 1
Epoch: 0
Summary: ADAPTIVE Communication Environment
URL: http://www.cs.wustl.edu/~schmidt/ACE.html
Source0: http://download.dre.vanderbilt.edu/ACE+TAO-distribution/ACE-src.tar.bz2
License: BSD-style
Group: System/Libraries
Requires(post): info-install
Requires(preun): info-install
BuildRequires:  libopenssl-devel

%description
The ADAPTIVE Communication Environment (ACE) is a freely available,
open-source object-oriented (OO) framework that implements many core
patterns for concurrent communication software. ACE provides a rich set
of reusable C++ wrapper facades and framework components that perform
common communication software tasks across a range of OS platforms. The
communication software tasks provided by ACE include event
demultiplexing and event handler dispatching, signal handling, service
initialization, interprocess communication, shared memory management,
message routing, dynamic (re)configuration of distributed services,
concurrent execution and synchronization.

#----------------------------------------------------------------------------

%package -n %{lib_name}
Summary: Main library for ACE (ADAPTIVE Communication Environment)
Group: System/Libraries

%description -n %{lib_name}
This package contains the libraries needed to run programs dynamically linked
with ACE (ADAPTIVE Communication Environment).

%post -n %{lib_name} -p /sbin/ldconfig
%postun -n %{lib_name} -p /sbin/ldconfig

%files -n %{lib_name}
%defattr(-,root,root)
%doc ACE-INSTALL.html AUTHORS ChangeLog COPYING FAQ NEWS PROBLEM-REPORT-FORM README THANKS VERSION
%{_libdir}/*-%{version}.so

#----------------------------------------------------------------------------

%package -n %{lib_name_devel}
Group: Development/C++
Summary: Shared libraries and header files for ACE (ADAPTIVE Communication Environment)
Obsoletes: %{mklibname ace 5 -d} < %{epoch}:%{version}-%{release}
Provides: %{name}-devel = %{epoch}:%{version}-%{release}
Provides: gperf-ace = %{epoch}:%{version}-%{release}
Requires: %{lib_name} = %{epoch}:%{version}-%{release}

%description -n %{lib_name_devel}
The %{name} package contains the shared libraries and header files needed for
developing ACE (ADAPTIVE Communication Environment) applications.

%post -n %{lib_name_devel}
%_install_info gperf-ace.info
%preun -n %{lib_name_devel}
%_remove_install_info gperf-ace.info

%files -n %{lib_name_devel}
%defattr(-,root,root)
%doc ChangeLogs README.gperf
%{_bindir}/*
%{_mandir}/man1/*
%{_infodir}/*
%{_includedir}/%{name}
%multiarch %{multiarch_includedir}/*
%{_includedir}/ACEXML
%{_includedir}/Kokyu
%{_libdir}/*.so
%{_libdir}/*.*a
%{_libdir}/pkgconfig/*

#----------------------------------------------------------------------------

%package -n %{name}-doc
Group:          Books/Howtos
Summary:        Documentation and examples for ACE (ADAPTIVE Communication Environment)
Obsoletes:      %{lib_name}-doc < %{epoch}:%{version}-%{release}
Provides:       %{lib_name}-doc = %{epoch}:%{version}-%{release}

%description -n %{name}-doc
Documentation and examples for ACE (ADAPTIVE Communication Environment).

%files -n %{name}-doc
%defattr(-,root,root)
%doc docs examples

#----------------------------------------------------------------------------

%prep
%setup -q -n ACE_wrappers
%{_bindir}/find examples -type f -name "*.ds[pw]" -o -name "*.sln" -o -name "*.vc[pw]" -o -name "*.vcproj" -o -name "*.bor" | \
  %{_bindir}/xargs perl -pi -e 's|\r$||g'
chmod 755 examples/IPC_SAP/SOCK_SAP/run_test

%build
%{_bindir}/autoreconf -i -v -f

# Lack of proper config way requires some sed trick to get functionalities enabled
# THREAD_SAFE_ACCEPT
sed -i "s/^#undef ACE_HAS_THREAD_SAFE_ACCEPT.*/#define ACE_HAS_THREAD_SAFE_ACCEPT/g" ace/config.h.in

export CPPFLAGS="${CPPFLAGS} %{optflags} -fPIC -DPIC"

mkdir -p objdir
(cd objdir && \
ln -sf ../configure .
%{configure2_5x} \
   --enable-lib-all \
   --disable-qos
%{make}
)

%install
rm -rf %{buildroot}

(cd objdir && %{makeinstall_std})

# The install script is incomplete (to be polite)

# gperf is provided by a different rpm
mv -f %{buildroot}%{_bindir}/gperf %{buildroot}%{_bindir}/gperf-ace

cat > README.gperf << EOF
ACE provides its own version of gperf which has been renamed to
gperf-ace to avoid a conflict with the gperf rpm. To use this
program, you must define  ACE_GPERF="%{_bindir}/gperf-ace" at
compile time.
EOF

# man and info pages
mkdir -p %{buildroot}%{_infodir}
install -m 644 apps/gperf/gperf.info %{buildroot}%{_infodir}/gperf-ace.info
perl -pi -e 's/gperf/gperf-ace/g;' -e 's/Gperf/Gperf-Ace/g;' \
              -e 's/GPERF/GPERF-ACE/g;' %{buildroot}%{_infodir}/gperf-ace.info
mkdir -p %{buildroot}%{_mandir}/man1
install -m 644 apps/gperf/gperf.1 %{buildroot}%{_mandir}/man1/gperf-ace.1
rm -f %{buildroot}%{_mandir}/man1/gperf.1

# Shameless adaptation from Debian rules
install -m 755 bin/generate_export_file.pl %{buildroot}%{_bindir}

files=`grep -lr defined.*ACE_TEMPLATES_REQUIRE_SOURCE ace | %{__sed} -e 's/^\.//' -e 's/.h$/.cpp/'`
for i in $files ; do
    if [ ! -f %{buildroot}%{_includedir}/$i -a -f $i ] ; then
        install -m 644 $i %{buildroot}%{_includedir}/`dirname $i`
    fi
done

files=`grep -lr defined.*ACE_TEMPLATES_REQUIRE_SOURCE Kokyu | %{__sed} -e 's/^\.//' -e 's/.h$/.cpp/'`
for i in $files ; do
    if [ ! -f %{buildroot}%{_includedir}/$i -a -f $i ] ; then
        install -m 644 $i %{buildroot}%{_includedir}/`dirname $i`
    fi
done

# I hope that's all we need

# fix location of .pc files
if test x"%{_libdir}" != "x%{_prefix}/lib"; then
    if test -d %{buildroot}%{_prefix}/lib/pkgconfig; then
        for i in %{buildroot}%{_prefix}/lib/pkgconfig/*.pc; do
          mv -f $i %{buildroot}%{_libdir}/pkgconfig
        done

        rm -rf %{buildroot}%{_prefix}/lib/pkgconfig
    fi
fi

# multiarch
%multiarch_includes %{buildroot}%{_includedir}/ace/config-borland-common.h
%multiarch_includes %{buildroot}%{_includedir}/ace/config.h
%multiarch_includes %{buildroot}%{_includedir}/ace/config-win32-common.h
%multiarch_includes %{buildroot}%{_includedir}/ace/config-win32-ghs.h

%clean
rm -rf %{buildroot}



