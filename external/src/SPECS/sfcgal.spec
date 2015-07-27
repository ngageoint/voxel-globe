%include %{_sourcedir}/common.inc

Name:		SFCGAL
Version:	1.0.5
Release:	1%{?dist}
Summary:	C++ wrapper library around CGAL
Source:		%{name}-%{version}.tar.gz
Source1:        common.inc

License:	LGPLv2+
Group:		Development/Libraries
URL: 		http://oslandia.github.io/SFCGAL/
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root
BuildRequires:	cgal >= 4.1
BuildRequires:  gmp >= 4.2
BuildRequires:	cmake >= 2.8.6
BuildRequires:  boost >= 1.46
BuildRequires:	mpfr >= 2.2.1

%description
SFCGAL provides standard compliant geometry types and operations, that can be accessed from its C or C++ APIs. PostGIS uses the C API, to expose some SFCGAL's functions in spatial databases (cf. PostGIS manual).

Geometry coordinates have an exact rational number representation and can be either 2D or 3D. Among supported geometry types are :

Points
LineStrings
Polygons
TriangulatedSurfaces
PolyhedralSurfaces
GeometryCollections
Solids
Supported operations include :

WKT reading and writing with exact rational number representation for coordinates
Intersection operations and predicates
Convex hull computation
Tessellation
Extrusion
Area and distance computation
Minkovski sums
Contour offsets
Straight skeleton generations

%prep
%setup -q -n %{name}-%{version}

%build
export GMP_DIR=%{install_dir}%{cat_prefix}
export MPFR_DIR=%{install_dir}%{cat_prefix}
export CGAL_DIR=%{install_dir}%{cat_prefix}
export BOOST_ROOT=%{install_dir}%{cat_prefix}
export BLAS_DIR=%{install_dir}%{cat_prefix}
export LAPACK_DIR=%{install_dir}%{cat_prefix}

mkdir -p build
pushd build

%{__cmake} -DCMAKE_VERBOSE_MAKEFILE=ON \
      -G "Unix Makefiles" \
      -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_INSTALL_PREFIX:PATH=%{cat_prefix} \
      -DCMAKE_INSTALL_LIBDIR=%{_libdir} \
      -DBoost_NO_BOOST_CMAKE=1 \
      ..

make %{_smp_mflags}

popd

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

pushd build
make install DESTDIR=$RPM_BUILD_ROOT
popd

mkdir -p $RPM_BUILD_ROOT%{_libdir}/la
mv $RPM_BUILD_ROOT%{_libdir}/*.la $RPM_BUILD_ROOT%{_libdir}/la

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%exclude /usr/lib/debug
/

%post

%postun

#%changelog

