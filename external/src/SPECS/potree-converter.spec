%include %{_sourcedir}/common.inc
Source999:        common.inc
%define real_name potree-converter
Name: %{real_name}%{name_suffix}
Provides: %{real_name}%{provides_suffix}

License:      BSD
Group:        Development/Languages/Other
Summary:      Builds a potree octree from las, laz, binary ply, xyz or ptx files.
Version:      1.3.1
Release:      1%{?dist}
URL:          http://potree.org/
BuildRoot:    %{_tmppath}/%{name}-%{version}-build
Source0:      https://github.com/potree/PotreeConverter/archive/1.3.1/%{real_name}-%{version}.tar.gz
BuildRequires: cmake
BuildRequires: gcc%{name_suffix} >= 4.9.0
BuildRequires: boost-devel
BuildRequires: lastools-laslib-devel
BuildRequires: lastools-laszip-devel
Requires:      lastools-laszip
Requires:      boost-program-options, boost-system, boost-regex, boost-thread, boost-filesystem


%description
Builds a potree octree from las, laz, binary ply, xyz or ptx files.

%prep
%setup -q -n PotreeConverter-%{version}

%build
mkdir -p build
pushd build

%{__cmake} -DCMAKE_BUILD_TYPE=Release \
           -DCMAKE_INSTALL_PREFIX:PATH=%{_prefix} \
           -DCMAKE_CXX_COMPILER=%{install_dir}%{_bindir}/c++ \
           -DLASZIP_LIBRARY=laszip \
           -DBoost_INCLUDE_DIR=%{install_dir}%{_includedir} \
           -DBoost_LIB_DIR=%{install_dir}%{_libdir} \
           ..

%{__make} %{?_smp_mflags} DESTDIR="%{buildroot}"
popd

%install

pushd build
  %{__make} install DESTDIR="%{buildroot}"
popd

%files
%{_bindir}/PotreeConverter