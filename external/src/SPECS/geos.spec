%include %{_sourcedir}/common.inc

Name:		geos
Version:	3.4.2
Release:        1%{?dist}
Summary:	GEOS is a C++ port of the Java Topology Suite

Group:		Applications/Engineering
License:	LGPLv2
URL:		http://trac.osgeo.org/geos/
Source0:	http://download.osgeo.org/geos/%{name}-%{version}.tar.bz2
Source1:	common.inc
Patch0:		geos-gcc43.patch

BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:	doxygen libtool
BuildRequires:	python-devel
BuildRequires:	gcc-c++

%description
GEOS (Geometry Engine - Open Source) is a C++ port of the Java Topology 
Suite (JTS). As such, it aims to contain the complete functionality of 
JTS in C++. This includes all the OpenGIS "Simple Features for SQL" spatial 
predicate functions and spatial operators, as well as specific JTS topology 
functions such as IsValid()

%package devel
Summary:	Development files for GEOS
Group:		Development/Libraries
Requires: 	%{name} = %{version}-%{release}

%description devel
GEOS (Geometry Engine - Open Source) is a C++ port of the Java Topology 
Suite (JTS). As such, it aims to contain the complete functionality of 
JTS in C++. This includes all the OpenGIS "Simple Features for SQL" spatial 
predicate functions and spatial operators, as well as specific JTS topology 
functions such as IsValid()

This package contains the development files to build applications that 
use GEOS

%package python
Summary:	Python modules for GEOS
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description python
Python module to build applications using GEOS and python

%prep
%setup -q
%patch0 -p0 -b .gcc43

sed -i 's|^#!/bin/sh$|#!/usr/bin/env bash|' tools/geos-config.in
sed -i 's|@prefix@|$(cd $(dirname $(readlink -f ${BASH_SOURCE[0]}))/%{prefix_bin_rel}; pwd)|' tools/geos-config.in
sed -i 's|@exec_prefix@|$(cd $(dirname $(readlink -f ${BASH_SOURCE[0]}))/%{exec_prefix_bin_rel}; pwd)|' tools/geos-config.in
sed -i 's|@libdir@|${prefix}/%{lib_prefix_rel}|' tools/geos-config.in

sed -i -r '/bool.*/ {N; s/(bool.DistanceOp::isWithinDistance)/#pragma GCC optimize ("O1")\n\1/}' ./src/operation/distance/DistanceOp.cpp 
echo '#pragma GCC reset_options' >> ./src/operation/distance/DistanceOp.cpp

#Fix STUPID automake inability to detect prefix right. Use this since MY Python DOES PREFIX RIGHT!
sed -i 's:base_python_path=`echo.*`:base_python_path=`${PYTHON} -c "from distutils.sysconfig import get_config_var; print get_config_var(\\"prefix\\")"`:' configure

%build

# fix python path on 64bit
#sed -i -e 's|\/lib\/python|$libdir\/python|g' configure
#sed -i -e 's|.get_python_lib(0|.get_python_lib(1|g' configure

# disable internal libtool to avoid hardcoded r-path
#for makefile in `find . -type f -name 'Makefile.in'`; do
#sed -i 's|@LIBTOOL@|%{_bindir}/libtool|g' $makefile
#done

export PYTHON=%{__python}
%{add_install_flags}

%configure --disable-dependency-tracking --enable-python
# Touch the file, since we are not using ruby bindings anymore:
# Per http://lists.osgeo.org/pipermail/geos-devel/2009-May/004149.html
touch swig/python/geos_wrap.cxx

make %{?_smp_mflags}

# Make doxygen documentation files
cd doc
make doxygen-html

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
make DESTDIR=%{buildroot} install

###mkdir %{_libdir}/la
###cp %{_libdir}/*.la %{_libdir}/la 

%check

# test module
make %{?_smp_mflags} check || exit 0

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%post

%postun

%files
%doc AUTHORS COPYING NEWS README TODO
%{_libdir}/libgeos-%{version}.so
%{_libdir}/libgeos_c.so.*
%{_libdir}/*.a

%files devel
%doc doc/doxygen_docs
%{_bindir}/geos-config
%{_includedir}/*
%{_libdir}/libgeos.so
%{_libdir}/libgeos_c.so
%exclude %{_libdir}/*.la
###%{_libdir}/la
#All the spec files exclude it, PLUS it confuses gdal because this is not as flexible as geos-config

%files python
%dir %{python_sitearch}/%{name}
%{python_sitearch}/%{name}/_%{name}.a
%{python_sitearch}/%{name}/_%{name}.la
%{python_sitearch}/%{name}.pth
%{python_sitearch}/%{name}/*.py
%{python_sitearch}/%{name}/*.py?
%{python_sitearch}/%{name}/_%{name}.so

%changelog
* Mon Sep 9 2013 Devrim GUNDUZ <devrim@gunduz.org> - 3.4.2-1
- Update to 3.4.2, per changes described at:
  http://trac.osgeo.org/geos/browser/tags/3.4.2/NEWS
- Remove Ruby bindings, per suggestion from Kashif Rasul.

* Tue Aug 20 2013 Devrim GUNDUZ <devrim@gunduz.org> - 3.4.1-1
- Update to 3.4.1, per changes described at:
  http://trac.osgeo.org/geos/browser/tags/3.4.1/NEWS

* Sun Aug 11 2013 Devrim GUNDUZ <devrim@gunduz.org> - 3.4.0-1
- Update to 3.4.0, per changes described at:
  http://trac.osgeo.org/geos/browser/tags/3.4.0/NEWS

* Thu Mar 14 2013 Devrim GUNDUZ <devrim@gunduz.org> - 3.3.8-1
- Update to 3.3.8, per changes described at:
  http://trac.osgeo.org/geos/browser/tags/3.3.8/NEWS
- Add new subpackage: ruby

* Tue Jan 15 2013 Devrim GÜNDÜZ <devrim@gunduz.org> - 3.3.6-4
- Final attempt to fix SIGABRT, per testing and patch by Klynton Jessup.

* Mon Jan 07 2013 Devrim GÜNDÜZ <devrim@gunduz.org> - 3.3.6-3
- Apply a better fix for SIGABRT, per
  http://trac.osgeo.org/geos/ticket/377#comment:4.

* Sun Jan 06 2013 Devrim GÜNDÜZ <devrim@gunduz.org> - 3.3.6-2
- Fix SIGABRT with GEOSDistance_r, per http://trac.osgeo.org/geos/ticket/377.

* Mon Dec 10 2012 Devrim GUNDUZ <devrim@gunduz.org> - 3.3.6-1
- Update to 3.3.6, per changes described at:
  http://trac.osgeo.org/geos/browser/tags/3.3.6/NEWS

* Tue Jul 3 2012 Devrim GUNDUZ <devrim@gunduz.org> - 3.3.5-1
- Update to 3.3.5, per changes described at:
  http://trac.osgeo.org/geos/browser/tags/3.3.5/NEWS

* Fri Jun 1 2012 Devrim GUNDUZ <devrim@gunduz.org> - 3.3.4-1
- Update to 3.3.4

* Wed Apr 4 2012 Devrim GUNDUZ <devrim@gunduz.org> - 3.3.3-1
- Update to 3.3.3

* Mon Jan 9 2012 Devrim GUNDUZ <devrim@gunduz.org> - 3.3.2-1
- Update to 3.3.2

* Tue Oct 4 2011 Devrim GUNDUZ <devrim@gunduz.org> - 3.3.1-1
- Update to 3.3.1

* Tue Aug 9 2011 Devrim GUNDUZ <devrim@gunduz.org> - 3.3.0-1
- Update to 3.3.0

* Thu May 27 2010 Devrim GUNDUZ <devrim@gunduz.org> - 3.2.2-1
- Update to 3.2.2

* Mon Jun 29 2009 Devrim GUNDUZ <devrim@gunduz.org> - 3.1.1-1
- Update to 3.1.1

* Tue Dec 2 2008 Devrim GUNDUZ <devrim@gunduz.org> - 3.0.3-1
- Update to 3.0.3
- Remove patch 1 -- it is now in upstream.

* Mon Jun 2 2008 Devrim GUNDUZ <devrim@gunduz.org> - 3.0.0-4
- Sync with Fedora spec file.

* Wed May 28 2008 Balint Cristian <rezso@rdsor.ro> - 3.0.0-4
- disable bindings for REL4

* Wed Apr 23 2008 Balint Cristian <rezso@rdsor.ro> - 3.0.0-3
- require ruby too

* Wed Apr 23 2008 Balint Cristian <rezso@rdsor.ro> - 3.0.0-2
- remove python-abi request, koji fails

* Sun Apr 20 2008 Balint Cristian <rezso@rdsor.ro> - 3.0.0-1
- New branch upstream
- Fix gcc43 build
- Avoid r-path hardcoding
- Enable and include python module
- Enable and include ruby module
- Enable and run testsuite during build

* Thu Apr 3 2008 Devrim GUNDUZ <devrim@gunduz.org> - 0:2.2.3-2
- Initial build for pgsqlrpms.org, based on Fedora/EPEL spec.

