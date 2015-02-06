Name:		ace
Version:	5.8.1
Release:	3
Summary:	ADAPTIVE Communication Environment
License: 	BSD-style
Group:		System/Libraries
URL:		http://www.cs.wustl.edu/~schmidt/ACE.html
Source0:	http://download.dre.vanderbilt.edu/previous_versions/ACE-src-%{version}.tar.bz2
Patch1:		ACE-5.8.1-link.patch
Patch2:		ACE-5.8.1-ssl-1.0.patch
BuildRequires:	pkgconfig(openssl)

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

%define lib_major 5
%define lib_name %mklibname %{name} %{lib_major}

%package -n %{lib_name}
Summary: Main library for ACE (ADAPTIVE Communication Environment)
Group: System/Libraries

%description -n %{lib_name}
This package contains the libraries needed to run programs dynamically linked
with ACE (ADAPTIVE Communication Environment).

%files -n %{lib_name}
%{_libdir}/*-%{version}.so

#----------------------------------------------------------------------------

%define lib_name_devel  %mklibname %{name} -d

%package -n %{lib_name_devel}
Group:		Development/C++
Summary:	Shared libraries and header files for ACE (ADAPTIVE Communication Environment)
Provides:	%{name}-devel = %{version}-%{release}
Requires:	%{lib_name} = %{version}-%{release}

%description -n %{lib_name_devel}
The %{name} package contains the shared libraries and header files 
needed for developing ACE (ADAPTIVE Communication Environment) applications.

%files -n %{lib_name_devel}
%doc ACE-INSTALL.html AUTHORS ChangeLog COPYING FAQ NEWS PROBLEM-REPORT-FORM README THANKS VERSION
%{_bindir}/*
%{_mandir}/man1/*
%{_includedir}/%{name}
%{_includedir}/ACEXML
%{_includedir}/Kokyu
%{_libdir}/*.so
%{_libdir}/pkgconfig/*
%exclude %{_libdir}/*-%{version}.so

#----------------------------------------------------------------------------

%define lib_name_devel_stat  %mklibname %{name} -d -s

%package -n %{lib_name_devel_stat}
Group:		Development/C++
Summary:	Shared libraries and header files for ACE (ADAPTIVE Communication Environment)
Requires:	%{lib_name_devel} = %{version}-%{release}

%description -n %{lib_name_devel_stat}
The %{name} package contains the shared libraries and header files 
needed for developing ACE (ADAPTIVE Communication Environment) applications.

%files -n %{lib_name_devel_stat}
%{_libdir}/*.a

#----------------------------------------------------------------------------

%package -n %{name}-doc
Group:		Books/Howtos
Summary:	Documentation and examples for ACE (ADAPTIVE Communication Environment)

%description -n %{name}-doc
Documentation and examples for ACE (ADAPTIVE Communication Environment).

%files -n %{name}-doc
%doc docs examples

#----------------------------------------------------------------------------

%prep
%setup -q -n ACE_wrappers
%patch1 -p0 -b .link
%patch2 -p0 -b .ssl

%build
autoreconf -i -v -f

export CONFIGURE_TOP=${PWD}

mkdir -p build
cd build 
%configure2_5x \
   --enable-lib-all \
   --enable-static \
   --enable-symbol-visibility \
   --disable-qos \
   --with-openssl=%{_prefix} \
   --with-openssl-include=%{_includedir} \
   --with-openssl-libdir=%{_libdir}
%make
cd -

%install
%makeinstall_std -C build

# The install script is incomplete (to be polite)

# Shameless adaptation from Debian rules
install -m 755 bin/generate_export_file.pl %{buildroot}%{_bindir}

files=`grep -lr defined.*ACE_TEMPLATES_REQUIRE_SOURCE ace | sed -e 's/^\.//' -e 's/.h$/.cpp/'`
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

