%include %{_sourcedir}/common.inc

Summary: Numerical linear algebra package libraries
Name: lapack
Version: 3.5.0
Release: 1%{?dist}
License: BSD
Group: Development/Libraries
URL: http://www.netlib.org/lapack/
Source0: http://www.netlib.org/lapack/lapack-%{version}.tgz
Source1: common.inc
Source2: %{name}-%{version}_manpages.tgz
BuildRequires: gcc-gfortran
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%description
LAPACK (Linear Algebra PACKage) is a standard library for numerical
linear algebra. LAPACK provides routines for solving systems of
simultaneous linear equations, least-squares solutions of linear
systems of equations, eigenvalue problems, and singular value
problems. Associated matrix factorizations (LU, Cholesky, QR, SVD,
Schur, and generalized Schur) and related computations (i.e.,
reordering of Schur factorizations and estimating condition numbers)
are also included. LAPACK can handle dense and banded matrices, but
not general sparse matrices. Similar functionality is provided for
real and complex matrices in both single and double precision. LAPACK
is coded in Fortran77 and built with gcc.

%package devel
Summary: LAPACK development libraries
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}
Requires: blas-devel = %{version}-%{release}
#NOT TRUE Provides: lapack-static = %{version}-%{release}

%description devel
LAPACK development libraries for applications that link statically.

%package  blas
Summary: The Basic Linear Algebra Subprograms library
Group: Development/Libraries

%description blas
BLAS (Basic Linear Algebra Subprograms) is a standard library which
provides a number of basic algorithms for numerical algebra. 

%package blas-devel
Summary: BLAS development libraries
Group: Development/Libraries
Requires: blas = %{version}-%{release}
Requires: gcc-gfortran
Provides: blas-static = %{version}-%{release}

%description blas-devel
BLAS development libraries for applications that link statically.

%prep
%setup -q

%build
#autoreconf --force --install
mkdir build
pushd build
%{__cmake} -DCMAKE_VERBOSE_MAKEFILE=ON \
      -DCMAKE_INSTALL_LIBDIR:PATH=%{_libdir} \
      -G "Unix Makefiles" \
      -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_INSTALL_PREFIX:PATH=%{cat_prefix} \
      -DINCLUDE_INSTALL_DIR:PATH=%{_includedir} \
      -DSYSCONF_INSTALL_DIR:PATH=%{_sysconfdir} \
      -DSHARE_INSTALL_PREFIX:PATH=%{_datadir} \
      -DCMAKE_Fortran_FLAGS=-fPIC \
      -DBUILD_SHARED_LIBS=ON \
      -DCMAKE_Fortran_COMPILER=`which gfortran` \
      -DPYTHON_EXECUTABLE=%{__python} \
      ..

#      -DUSE_OPTIMIZED_BLAS=ON \
#      -DUSE_OPTIMIZED_LAPACK=ON \

#If you do -DCMAKE_INSTALL_PREFIX:PATH=%{_prefix} too, cmake will BREAK

make %{_smp_mflags} DESTDIR="%{buildroot}"

lapack_objs=( $(cat SRC/CMakeFiles/lapack.dir/link.txt) )
blas_objs=( $(cat BLAS/SRC/CMakeFiles/blas.dir/link.txt) )

lapack_objs=( $(for i in ${lapack_objs[@]}
do
  echo $i
done | \grep \\.f\\.o) )

blas_objs=( $(for i in ${blas_objs[@]}
do
  echo $i
done | \grep \\.f\\.o) )

pushd SRC
ar ruv ../lib/liblapack.a ${lapack_objs[@]}
ranlib ../lib/liblapack.a 
popd

pushd BLAS/SRC
ar ruv ../../lib/libblas.a ${blas_objs[@]}
ranlib ../../lib/libblas.a 
popd

popd

%check
LD_LIBRARY_PATH=`pwd`${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
export LD_LIBRARY_PATH
pushd build
%{add_install_path}
make test || exit 0
popd

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
pushd build
make install DESTDIR="%{buildroot}"
popd

pushd ${RPM_BUILD_ROOT}%{_libdir}

mv liblapack.so liblapack.so.%{version}
ln -s liblapack.so.%{version} liblapack.so.${RPM_PACKAGE_VERSION%.*.*}
ln -s liblapack.so.%{version} liblapack.so

mv libblas.so libblas.so.%{version}
ln -s libblas.so.%{version} libblas.so.${RPM_PACKAGE_VERSION%.*.*}
ln -s libblas.so.%{version} libblas.so

mv libtmglib.so libtmglib.so.%{version}
ln -s libtmglib.so.%{version} libtmglib.so.${RPM_PACKAGE_VERSION%.*.*}
ln -s libtmglib.so.%{version} libtmglib.so

popd

mkdir -p ${RPM_BUILD_ROOT}%{_mandir}
chmod 755 ${RPM_BUILD_ROOT}%{_mandir}
pushd ${RPM_BUILD_ROOT}%{_mandir}
tar -zxvf %{SOURCE2}

popd

install -p -m 0755 build/lib/liblapack.a ${RPM_BUILD_ROOT}%{_libdir}/liblapack.a
install -p -m 0755 build/lib/libblas.a ${RPM_BUILD_ROOT}%{_libdir}/libblas.a

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%{_mandir}
%{_libdir}/liblapack.so.*
%{_libdir}/libtmglib.so.*

%files devel
%{_libdir}/liblapack.so
%{_libdir}/libtmglib.so
%{_libdir}/liblapack.a
%{_libdir}/cmake
%{_libdir}/pkgconfig

%files blas
%{_libdir}/libblas.so.*

%files blas-devel
%{_libdir}/libblas.so
%{_libdir}/libblas.a

%post

%postun

#%changelog

