%define name plyfile
%define version 0.4
%define unmangled_version 0.4
%define unmangled_version 0.4
%define release 1

Summary: PLY file reader/writer
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{unmangled_version}.tar.gz
License: GPLv3
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Darsh Ranjan <darsh.ranjan@here.com>
Url: https://github.com/dranjan/python-plyfile

%description
Python module, which provides a simple facility for reading and writing ASCII and binary PLY files.

%prep
%setup -n %{name}-%{unmangled_version} -n %{name}-%{unmangled_version}

%build
python setup.py build

%install
python setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
