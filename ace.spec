%define name	ace
%define Name	ACE
%define version	5.5.2
%define release	%mkrel 4

%define lib_major	5
%define lib_name_orig	%mklibname %{name}
%define lib_name	%{lib_name_orig}%{lib_major}

Summary:	ADAPTIVE Communication Environment
Name:		%{name}
Version:	%{version}
Release:	%{release}
Epoch:		0
URL:		http://www.cs.wustl.edu/~schmidt/ACE.html
Source0:	http://deuce.doc.wustl.edu/%{Name}.tar.bz2
Patch0: ace-5.5.2-osinl.patch
Patch1: ace-5.5.2-safe_thread.patch
License:	BSD-style
Group:		System/Libraries
Requires(post):	/sbin/install-info
Requires(preun): /sbin/install-info
BuildRequires:	openssl-devel
Buildroot:	%{_tmppath}/%{name}-%{version}-%{release}-root

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

#------------------------------------------------------------------------------

%package -n %{lib_name}
Summary:        Main library for ACE (ADAPTIVE Communication Environment)
Group:          System/Libraries

%description -n %{lib_name}
This package contains the libraries needed to run programs dynamically linked
with ACE (ADAPTIVE Communication Environment).

%files -n %{lib_name}
%defattr(-,root,root)
%doc ACE-INSTALL ACE-INSTALL.html AUTHORS ChangeLog COPYING FAQ PROBLEM-REPORT-FORM README THANKS VERSION
%{_libdir}/*.so.*

#------------------------------------------------------------------------------

%package -n %{lib_name}-devel
Group:		Development/C++
Summary:	Shared libraries and header files for ACE (ADAPTIVE Communication Environment)
Provides:	%{name}-devel
Provides:	lib%{name}-devel
Provides:	%{_lib}%{name}-devel
Provides:       gperf-ace
Requires:	%{lib_name} = %{epoch}:%{version}
Requires:	openssl-devel

#------------------------------------------------------------------------------

%description -n %{lib_name}-devel
The %{name} package contains the shared libraries and header files needed for
developing ACE (ADAPTIVE Communication Environment) applications.

%package -n %{lib_name}-doc
Group:		Books/Howtos
Summary:        Documentation and examples for ACE (ADAPTIVE Communication Environment)

%description -n %{lib_name}-doc
Documentation and examples for ACE (ADAPTIVE Communication Environment).

%prep
%setup -q -n ACE_wrappers
%patch0 -p1 -b .osinl
%patch1 -p1 -b .thread
find examples -type f -name "*.ds[pw]" -o -name "*.sln" -o -name "*.vc[pw]" -o -name "*.vcproj" -o -name "*.bor" | \
  xargs perl -pi -e 's|\r$||g'
chmod 755 examples/IPC_SAP/SOCK_SAP/run_test


%build
export CFLAGS="${CFLAGS} %{optflags} -fPIC"
export CXXFLAGS="${CXXFLAGS} %{optflags} -fPIC"

mkdir -p objdir
(cd objdir && \
ln -s f ../configure .
%configure2_5x \
   --enable-lib-all \
   --disable-qos
%make
)

%install
rm -rf %{buildroot}

(cd objdir && %makeinstall_std)

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
%multiarch_includes %{buildroot}%{_includedir}/ace/config-win32-visualage.h

%clean
rm -rf %{buildroot}

%post -n %{lib_name} -p /sbin/ldconfig
%postun -n %{lib_name} -p /sbin/ldconfig

%post -n %{lib_name}-devel
%_install_info gperf-ace.info
%preun -n %{lib_name}-devel
%_remove_install_info gperf-ace.info


%files -n %{lib_name}-devel
%defattr(-,root,root)
%doc ChangeLogs README.gperf
%{_bindir}/*
%{_mandir}/man1/*
%{_infodir}/*
%{_includedir}/%{name}
%multiarch %{multiarch_includedir}/*
%{_includedir}/ACEXML
%{_includedir}/protocols
%{_includedir}/Kokyu
%{_libdir}/*.so
%{_libdir}/*.*a
%{_libdir}/pkgconfig/*

%files -n %{lib_name}-doc
%defattr(-,root,root)
%doc docs examples



