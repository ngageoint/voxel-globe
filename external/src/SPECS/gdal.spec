#with MUST come  BEFORE common.inc, or else variables are magically "wiped"?
%bcond_with opencl

%if %{with opencl}
  %define with_opencl 1
%else
  %define with_opencl 0
%endif

%include %{_sourcedir}/common.inc

Summary: Geospatial Data Abstraction Library
Name: gdal
Version: 1.11.2
Release: 1%{?dist}
License: MIT/X
Group: Applications/Engineering
URL: http://www.gdal.org/

Packager: Dries Verachtert <dries@ulyssis.org>
Vendor: Dag Apt Repository, http://dag.wieers.com/apt/

Source: http://download.osgeo.org/gdal/gdal-%{version}.tar.xz
Source1:        common.inc

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

BuildRequires: curl-devel
BuildRequires: gcc-c++
BuildRequires: geos-devel
BuildRequires: giflib-devel
BuildRequires: libjpeg-devel
BuildRequires: libpng-devel
BuildRequires: libtiff-devel
BuildRequires: netcdf-devel
BuildRequires: openssl-devel
BuildRequires: postgresql-devel
BuildRequires: python-devel

%if %{with_opencl}
BuildRequires: opencl-devel
%endif
#This is ok, but with with NO underscore, VERY BAD! RPM Bug? without _ MUST
#Come before the %include, or else

%description
The Geospatial Data Abstraction Library (GDAL) is a unifying C/C++ API for 
accessing raster geospatial data, and currently includes formats like 
GeoTIFF, Erdas Imagine, Arc/Info Binary, CEOS, DTED, GXF, and SDTS. It is 
intended to provide efficient access, suitable for use in viewer 
applications, and also attempts to preserve coordinate systems and 
metadata. Python, C, and C++ interfaces are available.

%package devel
Summary: Header files, libraries and development documentation for %{name}.
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}

%description devel
This package contains the header files, static libraries and development
documentation for %{name}. If you like to develop programs using %{name},
you will need to install %{name}-devel.

%package python
Summary: The Python bindings for the GDAL library
Group: Development/Python
Requires: %{name} = %{version}-%{release}

%description python
The Python bindings for the GDAL library

%prep
%setup -q

sed -i 's/GetGDALDriverManager()->GetDriverByName( "JPEG2000" )/GetGDALDriverManager()->GetDriverByName( "JP2OpenJpeg" )/' ./frmts/nitf/nitfdataset.cpp
#Make the GDAL writer work with openjpeg (Replacing the Jasper line), which does work!? *Shrugs*
sed -i 's|#!/bin/sh|#!/usr/bin/env bash|' ./apps/GNUmakefile

%build
%{add_install_flags}

%configure \
    --datadir="%{_datadir}/gdal" \
    --with-python=%{__python} \
    --with-geos=%{_roamdir}/geos-config \
%if %{with_opencl}
    --with-opencl=yes \
    --with-opencl-include=%{opencl_include_dir} \
    --with-opencl-lib="%{opencl_libflags}" \
%endif
    --with-libjson-c=%{install_dir}%{cat_prefix} \
    --with-openjpeg=%{install_dir}%{cat_prefix}


make -C apps gdal-config-inst \
  INST_PREFIX='$$(cd $$(dirname $$(readlink -f $${BASH_SOURCE[0]}))/%{prefix_bin_rel}; pwd)' \
  INST_INCLUDE='$${CONFIG_PREFIX}/%{include_prefix_rel}' \
  INST_DATA='$${CONFIG_PREFIX}/%{data_prefix_rel}' \
  INST_LIB='$$(cd $$(dirname $$(readlink -f $${BASH_SOURCE[0]}))/%{prefix_bin_rel}; pwd)/%{lib_prefix_rel}' \
  INST_BIN='$${CONFIG_PREFIX}/%{bin_prefix_rel}'

%{__make} %{?_smp_mflags}


%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
mkdir -p %{buildroot}%{python_sitearch}
env PYTHONPATH=%{buildroot}%{python_sitearch} %{__make} install DESTDIR="%{buildroot}" PY_HAVE_SETUPTOOLS=0

mkdir -p $RPM_BUILD_ROOT%{_libdir}/la
mv $RPM_BUILD_ROOT%{_libdir}/*.la $RPM_BUILD_ROOT%{_libdir}/la

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-, root, root, 0755)
%doc NEWS 
%doc man/man1
%{_bindir}/
%{_datadir}/gdal/
%{_libdir}/libgdal*
%exclude %{_libdir}/pkgconfig

%files python
%{python_sitearch}
%exclude %{python_sitearch}/site*
%{python_sitearch}/easy-install.pth


%files devel
%defattr(-, root, root, 0755)
%{_includedir}/cpl*.h
%{_includedir}/gdal*.h
%{_includedir}/ogr*.h
%{_includedir}/???dataset.h
%{_includedir}/gvgcpfit.h
%{_includedir}/thinplatespline.h
%{_libdir}/libgdal.so
%{_libdir}/la/*.la
#%exclude %{_libdir}/*.la

