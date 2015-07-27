%include %{_sourcedir}/common.inc

%{!?pgsql:%define pgsql 0}
%{!?perl:%define perl 0}
%{!?php:%define php 0}
%{!?dce:%define dce 0}

Name:		uuid
Version:	1.6.2
Release:	1%{?dist}
Summary:	Universally Unique Identifier library
Source:		%{name}-%{version}.tar.gz
Source1:        common.inc

License:	MIT
Group:		System Environment/Libraries
URL: 		http://www.ossp.org/pkg/lib/uuid/
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root
BuildRequires:	libtool

%description
OSSP uuid is a ISO-C:1999 application programming interface (API)
and corresponding command line interface (CLI) for the generation
of DCE 1.1, ISO/IEC 11578:1996 and RFC 4122 compliant Universally
Unique Identifier (UUID). It supports DCE 1.1 variant UUIDs of version
1 (time and node based), version 3 (name based, MD5), version 4
(random number based) and version 5 (name based, SHA-1). Additional
API bindings are provided for the languages ISO-C++:1998, Perl:5 and
PHP:4/5. Optional backward compatibility exists for the ISO-C DCE-1.1
and Perl Data::UUID APIs.

%package devel
Summary:        Development support for Universally Unique Identifier library
Group:          Development/Libraries
Requires:       pkgconfig
Requires:       %{name} = %{version}-%{release}

%description devel
Development headers and libraries for OSSP uuid.

%package c++
Summary:        C++ support for Universally Unique Identifier library
Group:          System Environment/Libraries
Requires:       %{name} = %{version}-%{release}

%description c++
C++ libraries for OSSP uuid.

%package c++-devel
Summary:        C++ development support for Universally Unique Identifier library
Group:          Development/Libraries
Requires:       %{name}-c++ = %{version}-%{release}
Requires:       %{name}-devel = %{version}-%{release}

%description c++-devel
C++ development headers and libraries for OSSP uuid.

%if %perl
%package perl
Summary:        Perl support for Universally Unique Identifier library
Group:          Development/Libraries
BuildRequires:  perl(ExtUtils::MakeMaker)
BuildRequires:  perl(Test::More)
Requires:       perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
Requires:       %{name} = %{version}-%{release}

%description perl
Perl OSSP uuid modules, which includes a Data::UUID replacement.
%endif

%if %php
%package php
Summary:        PHP support for Universally Unique Identifier library
Group:          Development/Libraries
BuildRequires:  php-devel
Requires:       %{name} = %{version}-%{release}
%if 0%{?php_zend_api}
Requires: php(zend-abi) = %{php_zend_api}
Requires: php(api) = %{php_core_api}
%else
Requires: php-api = %{php_apiver}
%endif

%description php
PHP OSSP uuid module.
%endif

%if %pgsql
%package pgsql
Summary:        PostgreSQL support for Universally Unique Identifier library
Group:          Development/Libraries
BuildRequires:  postgresql-devel
Requires:       %{_libdir}/pgsql
Requires:       %{_datadir}/pgsql
Requires:       %{name} = %{version}-%{release}

%description pgsql
PostgreSQL OSSP uuid module.
%endif

%if %dce
%package dce
Summary:        DCE support for Universally Unique Identifier library
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}

%description dce
DCE OSSP uuid library.

%package dce-devel
Summary:        DCE development support for Universally Unique Identifier library
Group:          Development/Libraries
Requires:       %{name}-dce = %{version}-%{release}
Requires:       %{name}-devel = %{version}-%{release}

%description dce-devel
DCE development headers and libraries for OSSP uuid.
%endif

%prep
%setup -q -n %{name}-%{version}

sed -i 's|^#!/bin/sh$|#!/usr/bin/env bash|' uuid-config.in
sed -i 's|@prefix@|$(cd $(dirname $(readlink -f ${BASH_SOURCE[0]}))/%{prefix_bin_rel}; pwd)|' uuid-config.in
sed -i 's|@exec_prefix@|$(cd $(dirname $(readlink -f ${BASH_SOURCE[0]}))/%{exec_prefix_bin_rel}; pwd)|' uuid-config.in
sed -i 's|@bindir@|${prefix}/%{bin_prefix_rel}|' uuid-config.in
sed -i 's|@libdir@|${prefix}/%{lib_prefix_rel}|' uuid-config.in
sed -i 's|@includedir@|${prefix}/%{include_prefix_rel}|' uuid-config.in
sed -i 's|@mandir@|${prefix}/%{man_prefix_rel}|' uuid-config.in
sed -i 's|@datarootdir@|${prefix}/%{data_prefix_rel}|' uuid-config.in

%build

export LIB_NAME=libuuid.la
export DCE_NAME=libuuid_dce.la
export CXX_NAME=libuuid++.la
export PHP_NAME=$(pwd)/php/modules/uuid.so
export PGSQL_NAME=$(pwd)/pgsql/libuuid.so
%configure \
    --enable-static=yes \
    --enable-shared=yes \
    --without-perl \
    --without-php \
%if %dce
    --with-dce \
%endif
%if %pgsql
    --with-pgsql \
%endif
    --with-cxx
#    --disable-static \

make %{?_smp_mflags}

%if %perl
# Build the Perl module.
pushd perl
%{__perl} Makefile.PL INSTALLDIRS=vendor OPTIMIZE="$RPM_OPT_FLAGS" COMPAT=1
%{__perl} -pi -e 's/^\tLD_RUN_PATH=[^\s]+\s*/\t/' Makefile
make %{?_smp_mflags}
popd
%endif

%if %php
# Build the PHP module.
pushd php
export PHP_RPATH=no
phpize
CFLAGS="$RPM_OPT_FLAGS -I.. -L.. -L../.libs"
%configure --enable-uuid
make %{?_smp_mflags}
popd
%endif

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

make install DESTDIR=$RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{_libdir}/la
mv $RPM_BUILD_ROOT%{_libdir}/*.la $RPM_BUILD_ROOT%{_libdir}/la
#rm -f $RPM_BUILD_ROOT%{_libdir}/*.la #$RPM_BUILD_ROOT%{_libdir}/*.a
chmod 755 $RPM_BUILD_ROOT%{_libdir}/*.so.*.*.*

%if %perl
# Install the Perl modules.
pushd perl
make pure_install PERL_INSTALL_ROOT=$RPM_BUILD_ROOT

find $RPM_BUILD_ROOT -type f -name '*.bs' -size 0 -exec rm -f {} \;
find $RPM_BUILD_ROOT -type f -name .packlist -exec rm -f {} \;
find $RPM_BUILD_ROOT -depth -type d -exec rmdir {} 2>/dev/null \;

%{_fixperms} $RPM_BUILD_ROOT/*
popd
%endif

%if %php
# Install the PHP module.
pushd php
make install INSTALL_ROOT=$RPM_BUILD_ROOT
rm -f $RPM_BUILD_ROOT%{php_extdir}/*.a
popd

# Put the php config bit into place
%{__mkdir_p} %{buildroot}%{_sysconfdir}/php.d
%{__cat} << __EOF__ > %{buildroot}%{_sysconfdir}/php.d/%{name}.ini
; Enable %{name} extension module
extension=%{name}.so
__EOF__
%endif

%check
make check

%if %perl
pushd perl
LD_LIBRARY_PATH=../.libs make test
popd
%endif

%if %php
pushd php
LD_LIBRARY_PATH=../.libs make test
popd
%endif

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc AUTHORS ChangeLog HISTORY NEWS PORTING README SEEALSO THANKS TODO USERS
%{_bindir}/uuid
%{_libdir}/libuuid.so.*
%{_mandir}/man1/*

%files devel
%defattr(-,root,root,-)
%{_bindir}/uuid-config
%{_includedir}/uuid.h
%{_libdir}/libuuid.so
%{_libdir}/libuuid.a*
%{_libdir}/pkgconfig/uuid.pc
%{_mandir}/man3/uuid.3*
%{_libdir}/la/

%files c++
%defattr(-,root,root,-)
%{_libdir}/libuuid++.so.*

%files c++-devel
%defattr(-,root,root,-)
%{_includedir}/uuid++.hh
%{_libdir}/libuuid++.so
%{_libdir}/libuuid++.a*
%{_mandir}/man3/uuid++.3*

%if %perl
%files perl
%defattr(-,root,root,-)
%{perl_vendorarch}/auto/*
%{perl_vendorarch}/Data*
%{perl_vendorarch}/OSSP*
%{_mandir}/man3/Data::UUID.3*
%{_mandir}/man3/OSSP::uuid.3*
%endif

%if %php
%files php
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/php.d/%{name}.ini
%{php_extdir}/%{name}.so
%endif

%if %pgsql
%files pgsql
%defattr(-,root,root,-)
%{_libdir}/pgsql/*
%{_datadir}/pgsql/*
%endif

%if %dce
%files dce
%defattr(-,root,root,-)
%{_libdir}/libuuid_dce.so.*

%files dce-devel
%defattr(-,root,root,-)
%{_includedir}/uuid_dce.h
%{_libdir}/libuuid_dce.so
%endif
