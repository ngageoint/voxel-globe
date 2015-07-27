%include %{_sourcedir}/common.inc

Name:		CGAL
Version:	4.6
Release:	1%{?dist}
Summary:	Computational Geometry Algorithms Library
Source:		%{name}-%{version}.tar.bz2
Source1:        common.inc

License:	LGPL/GPL
Group:		Development/Libraries
URL: 		https://www.cgal.org/
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root
BuildRequires:  gmp-devel, mpfr-devel
BuildRequires:  boost, cmake

%description
The goal of the CGAL Open Source Project is to provide easy access to efficient and reliable geometric algorithms in the form of a C++ library. CGAL is used in various areas needing geometric computation, such as: computer graphics, scientific visualization, computer aided design and modeling, geographic information systems, molecular biology, medical imaging, robotics and motion planning, mesh generation, numerical methods... 

%prep
%setup -q -n %{name}-%{version}

%build
mkdir build
pushd build
export GMP_DIR=%{install_dir}%{cat_prefix}
export MPFR_DIR=%{install_dir}%{cat_prefix}
export BOOST_ROOT=%{install_dir}%{cat_prefix}
export BLAS_DIR=%{install_dir}%{cat_prefix}
export LAPACK_DIR=%{install_dir}%{cat_prefix}

%{__cmake} -DCMAKE_VERBOSE_MAKEFILE=ON \
      -G "Unix Makefiles" \
      -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_INSTALL_PREFIX:PATH=%{_prefix} \
      -DWITH_BLAS=ON \
      -DWITH_LAPACK=ON \
      -DBoost_NO_BOOST_CMAKE=1 \
      -DBLAS_INCLUDE_DIR=%{_includedir} \
      -DLAPACK_INCLUDE_DIR=%{_includedir} \
      -DWITH_CGAL_Qt3=OFF \
      -DWITH_CGAL_Qt4=OFF \
      -DBLAS_LIBRARIES_DIR=%{_libdir} \
      -DLAPACK_LIBRARIES_DIR=%{_libdir} \
      ..


make %{_smp_mflags} DESTDIR="%{buildroot}"
popd

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
pushd build
make install DESTDIR="%{buildroot}"
popd

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%exclude /usr/lib/debug
/

