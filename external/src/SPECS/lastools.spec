%include %{_sourcedir}/common.inc
Source999:        common.inc
%global real_name lastools
%global pretty_name LAStools
Name: %{real_name}%{name_suffix}
Provides: %{real_name}%{provides_suffix}

#%global rev 8b7be7da050afe41569fdc3ebd2250afef000df4
#Officially THEIR idea of a release... ;(
%global rev 8065ce39d50d09907691b5feda0267279428e586
#A sha from a different fork that actually works on linux :-\

License:      LGPL
Group:        Development/Other
Summary:      Software for rapid LiDAR processing
Version:      2015.10.09
Release:      1%{?dist}
URL:          http://www.cs.unc.edu/~isenburg/lastools/
Source0:      https://github.com/%{pretty_name}/%{pretty_name}/archive/%{rev}/%{real_name}-%{rev}.tar.gz

BuildRequires: gcc%{provides_suffix} >= 4.9
BuildRequires: cmake

%description
We provide an easy-to-use, ultra-light-weight, very efficient C++ programming API called 
LASlib (with LASzip DLL) that implements reading and writing of LiDAR points from and to 
the ASPRS LAS format (version 1.0-1.3) as well as its --- losslessly compressed, but 
otherwise identical twin --- the LAZ format. All source code (LGPL) is included.

%package laslib-devel
Provides: %{real_name}%{provides_suffix}-laslib-devel
Summary: C++ programming API for data stored in LAS/LAZ format
%description laslib-devel
LASlib (with LASzip) is a C++ programming API for reading / writing LIDAR
data stored in standard LAS or in compressed LAZ format (1.0 - 1.3). Both
libraries - LASlib with LASzip - are released together under the terms of
the GNU Lesser General Public Licence also known as LGPL.

%package laszip
Provides: %{real_name}%{provides_suffix}-laszip
Summary: Quickly turns bulky LAS files into compant LAZ files
%description laszip
LASzip - a free product of rapidlasso GmbH - quickly turns bulky LAS files into
compact LAZ files without information loss.

%package laszip-devel
Provides: %{real_name}%{provides_suffix}-laszip-devel
Summary: The development files for laszip
Requires: %{real_name}%{provides_suffix}-laszip
%description laszip-devel
Development headers and libraries for %{real_name}%{provides_suffix}-laszip

%prep
%setup -q -n %{pretty_name}-%{rev}

%build
make %{?_smp_mflags} COPTS="-O3 -Wall -Wno-deprecated -DNDEBUG -DUNORDERED -std=c++14"

mkdir -p LASzip/build
pushd LASzip/build
  cmake -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX:PATH=%{_prefix} \
        -DCMAKE_CXX_COMPILER=%{install_dir}%{_bindir}/c++ \
        ..
  %{__make} %{?_smp_mflags} DESTDIR="%{buildroot}"
popd

%install
mkdir -p "$RPM_BUILD_ROOT%{_bindir}"
mkdir -p "$RPM_BUILD_ROOT%{_docdir}/%{real_name}"
find bin -not -name '*.*' -exec install -D -p -m 755 \{\} %{buildroot}%{_bindir}/ \;
find bin -not -name '*.*' -exec install -D -p -m 755 \{\}_README.txt %{buildroot}%{_docdir}/%{real_name}/ \;

mkdir -p %{buildroot}%{_includedir}/
cp -a LASlib/inc/* %{buildroot}%{_includedir}/
cp -a LASzip/dll/*.h %{buildroot}%{_includedir}/

mkdir -p %{buildroot}%{_libdir}/
cp -a LASlib/lib/liblas.a %{buildroot}%{_libdir}/

mkdir -p "$RPM_BUILD_ROOT%{_libdir}"

mkdir -p "$RPM_BUILD_ROOT%{_includedir}"

cp -a LASzip/build/src/liblaszip.so "$RPM_BUILD_ROOT%{_libdir}"/liblaszip.so.%{version}
ln -s liblaszip.so.%{version} "$RPM_BUILD_ROOT%{_libdir}"/liblaszip.so.%(v=%{version}; echo ${v%%.*})
ln -s liblaszip.so.%(v=%{version}; echo ${v%%.*}) "$RPM_BUILD_ROOT%{_libdir}"/liblaszip.so
#pushd LASzip/build
#  %{__make} install  DESTDIR="%{buildroot}"
#popd

%files
%{_bindir}/*
%{_docdir}/%{real_name}

%files laslib-devel
%{_libdir}/liblas.a
%{_includedir}/*
%exclude %{_includedir}/laszip_dll.h

%files laszip-devel
%{_libdir}/liblaszip.so
%{_includedir}/laszip_dll.h

%files laszip
%{_libdir}/liblaszip.so.*
