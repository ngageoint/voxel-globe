%include %{_sourcedir}/common.inc

%{!?utils:%define	utils 1}
%{!?raster:%define	raster 1}

#Always check https://trac.osgeo.org/postgis/wiki/UsersWikiPostgreSQLPostGIS

Name:		postgis
Version:	2.1.7
Release:	1%{?dist}
Summary:	Geographic Information Systems Extensions to PostgreSQL
Source:		%{name}-%{version}.tar.gz
Source1:        common.inc
Source2:	http://download.osgeo.org/%{name}/docs/%{name}-%{version}.pdf

License:	GPLv2+
Group:		Applications/Databases
URL: 		http://www.postgis.net/
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root

BuildRequires:	postgresql%{pgmajorversion}-devel, proj-devel, geos-devel >= 3.4.2
BuildRequires:	proj-devel, flex, json-c-devel, libxml2-devel
%if %raster
BuildRequires:	gdal-devel
%endif

Requires:	postgresql%{pgmajorversion}, geos >= 3.4.2, proj, hdf5, json-c
Requires:	%{name}-client = %{version}-%{release}
Requires(post):	%{_sbindir}/update-alternatives

Provides:	%{name} = %{version}-%{release}

%description
PostGIS adds support for geographic objects to the PostgreSQL object-relational
database. In effect, PostGIS "spatially enables" the PostgreSQL server,
allowing it to be used as a backend spatial database for geographic information
systems (GIS), much like ESRI's SDE or Oracle's Spatial extension. PostGIS 
follows the OpenGIS "Simple Features Specification for SQL" and has been 
certified as compliant with the "Types and Functions" profile.

%package client
Summary:	Client tools and their libraries of PostGIS
Group:		Applications/Databases
Requires:       %{name}%{?_isa} = %{version}-%{release}
Provides:	%{name}-client = %{version}-%{release}

%description client
The postgis-client package contains the client tools and their libraries
of PostGIS.

%package devel
Summary:	Development headers and libraries for PostGIS
Group:		Development/Libraries
Requires:       %{name}%{?_isa} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}

%description devel
The postgis-devel package contains the header files and libraries
needed to compile C or C++ applications which will directly interact
with PostGIS.

%package docs
Summary:	Extra documentation for PostGIS
Group:		Applications/Databases

%description docs
The postgis-docs package includes PDF documentation of PostGIS.

%if %utils
%package utils
Summary:	The utils for PostGIS
Group:		Applications/Databases
Requires:	%{name} = %{version}-%{release}, perl-DBD-Pg
Provides:	%{name}-utils = %{version}-%{release}

%description utils
The postgis-utils package provides the utilities for PostGIS.
%endif

%prep
%setup -q -n %{name}-%{version}
# Copy .pdf file to top directory before installing.
cp -p %{SOURCE2} .

#sed -i 's/#include <json/#include <json-c/' liblwgeom/lwin_geojson.c
#sed -r -i 's/json_tokener_errors\[(.*)\]/json_tokener_error_desc\(\1\)/' liblwgeom/lwin_geojson.c

#sed -r -i 's|(-e "\$\{JSONDIR\}/lib/libjson.so" -o)|\1 -e "${JSONDIR}/lib/libjson-c.so" -o|' configure
#sed -r -i 's|(-e "\$\{JSONDIR\}/include/json/json.h" -o)|\\( \1 -e "${JSONDIR}/include/json-c/json.h" \\) -o|' configure

%build
# We need the below for GDAL:
export LD_LIBRARY_PATH=%{install_dir}%{_libdir}
export CPPFLAGS="${CPPFLAGS:+ ${CPPFLAGS}}-I%{install_dir}%{_includedir} -I%{install_dir}%{postgresql_includedir}/server"
export CFLAGS="${CFLAGS:+ ${CFLAGS}}-I%{install_dir}%{_includedir} -I%{install_dir}%{postgresql_includedir}/server"
./configure --with-pgconfig=%{_roamdir}/pg_config \
            --with-geosconfig=%{_roamdir}/geos-config \
            --with-gdalconfig=%{_roamdir}/gdal-config \
            --with-projdir=%{install_dir}%{cat_prefix} \
            --with-jsondir=%{install_dir}%{cat_prefix} \
%if !%raster
         --without-raster \
%endif
	 --disable-rpath \
         --libdir=%{postgresql_libdir} \
         --bindir=%{_bindir} \
         --includedir=%{postgresql_includedir} \
         --prefix=%{_prefix}

make %{?_smp_mflags} LPATH=`%{_roamdir}/pg_config --pkglibdir` shlib="%{name}.so"
make -C extensions

%if %utils
 make -C utils
%endif

%check
#env LD_LIBRARY_PATH=%{install_dir}%{_libdir}${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}} \
#    make check %{_smp_mflags}

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

make install DESTDIR=%{buildroot} PGSQL_BINDIR=%{_bindir} REGRESS=0 datadir=%{_datadir}/postgresql bindir=%{_bindir} pkglibdir=%{postgresql_libdir} includedir=%{postgresql_includedir} libdir=%{postgresql_libdir}
make -C extensions install DESTDIR=%{buildroot} PGSQL_BINDIR=%{_bindir} REGRESS=0 datadir=%{_datadir}/postgresql bindir=%{_bindir} pkglibdir=%{postgresql_libdir} includedir=%{postgresql_includedir} libdir=%{postgresql_libdir}

#mkdir -p %{buildroot}%{postgresql_libdir}
#mv %{buildroot}%{_libdir}/*.so %{buildroot}%{postgresql_libdir}
#I give up

%if %utils
install -d %{buildroot}%{_datadir}/%{name}
install -m 644 utils/*.pl %{buildroot}%{_datadir}/%{name}
%endif

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%doc COPYING CREDITS NEWS TODO README.%{name} doc/html loader/README.* doc/%{name}.xml doc/ZMSgeoms.txt
%{_datadir}/postgresql
%attr(755,root,root) %{postgresql_libdir}/%{name}-*.so
%{postgresql_libdir}/liblwgeom*.so
%if %raster
%{postgresql_libdir}/rtpostgis-*.so
%endif

%files client
%defattr(644,root,root)
%attr(755,root,root) %{_bindir}/*

%files devel
%defattr(644,root,root)
%{postgresql_includedir}
%{postgresql_libdir}/liblwgeom*.a
%{postgresql_libdir}/liblwgeom*.la

%if %utils
%files utils
%defattr(-,root,root)
%doc utils/README
%attr(755,root,root) %{_datadir}/%{name}/*.pl
%endif

%files docs
%defattr(-,root,root)
%doc %{name}-%{version}.pdf

%changelog
* Mon May 19 2014 Devrim GÜNDÜZ <devrim@gunduz.org> - 2.1.3-1
- Update to 2.1.3, for bug and security fixes.
- Bump up postgisprevversion to 2.0.6

* Wed Apr 2 2014 Devrim GÜNDÜZ <devrim@gunduz.org> - 2.1.2-2
- Bump up postgisprevversion to	2.0.5

* Sat Mar 29 2014 Devrim GÜNDÜZ <devrim@gunduz.org> - 2.1.2-1
- Update to 2.1.2

* Sat Nov 9 2013 Devrim GÜNDÜZ <devrim@gunduz.org> - 2.1.1-1
- Update to 2.1.1

* Mon Oct 7 2013 Devrim GÜNDÜZ <devrim@gunduz.org> - 2.1.0-4
- Install postgis-2.0.so file, by compiling it from 2.0 sources.
  Per lots of complaints to maintainers and pgsql-bugs lists.

* Mon Sep 23 2013 Devrim GÜNDÜZ <devrim@gunduz.org> - 2.1.0-3
- Rebuild against gdal 1.9.3, to fix extension related issues.
- Enable raster support in EL-6
- Let main package depend on client package. Per pgrpms #141
  and per PostgreSQL bug #8463.

* Tue Sep 10 2013 Devrim GÜNDÜZ <devrim@gunduz.org> - 2.1.0-2
- Remove ruby bindings, per
  http://lists.osgeo.org/pipermail/postgis-devel/2013-August/023690.html
- Move extension related files under main package,
  per report from Daryl Herzmann

* Mon Sep 9 2013 Devrim GÜNDÜZ <devrim@gunduz.org> - 2.1.0-1
- Update to 2.1.0

* Fri Aug 9 2013 Devrim GÜNDÜZ <devrim@gunduz.org> - 2.1.0rc2
- Update to 2.1.0rc2
- Remove patch0, it is now in upstream.

* Wed Jul 31 2013 Davlet Panech <dpanech@ubitech.com> - 2.1.0beta3-2
- Fixed "provides postgis" to avoid self-conflicts
- BuildRequires: libxml2-devel

* Sun Jun 30 2013 Devrim GÜNDÜZ <devrim@gunduz.org> - 2.1.0beta3-1
- Update to 2.1.0 beta3
- Support multiple version installation 
- Split "client" tools into a separate subpackage, per
  http://wiki.pgrpms.org/ticket/108
- Bump up alternatives version.
- Add dependency for mysql-devel, since Fedora / EPEL gdal packages
  are built with MySQL support, too. (for now). This is needed for
  raster support.
- Push raster support into conditionals, so that we can use similar 
  spec files for RHEL and Fedora.
- Add a patch to get rid of dependency hell from gdal. Per 
  http://lists.osgeo.org/pipermail/postgis-devel/2013-June/023605.html
  and a tweet from Mike Toews.

* Thu Apr 11 2013 Devrim GÜNDÜZ <devrim@gunduz.org> - 2.0.3-2
- Provide postgis, to satisfy OS dependencies. Per #79.

* Thu Mar 14 2013 Devrim GÜNDÜZ <devrim@gunduz.org> - 2.0.3-1
- Update to 2.0.3 

* Mon Dec 10 2012 Devrim GÜNDÜZ <devrim@gunduz.org> - 2.0.2-1
- Update to 2.0.2.
- Update download URL.
- Add deps for JSON-C support.

* Wed Nov 07 2012 Devrim GÜNDÜZ <devrim@gunduz.org> - 2.0.1-2
- Add dependency to hdf5, per report from Guillaume Smet.

* Wed Jul 4 2012 Devrim GUNDUZ <devrim@gunduz.org> - 2.0.0-1
- Update to 2.0.1, for changes described at:
  http://postgis.org/news/20120622/

* Tue Apr 3 2012 Devrim GUNDUZ <devrim@gunduz.org> - 2.0.0-1
- Initial packaging with PostGIS 2.0.0.
- Drop java bits from spec file.
