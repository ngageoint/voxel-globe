%include %{_sourcedir}/common.inc

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
Source1: common.inc
License: GPLv3
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildArch: noarch
Vendor: Darsh Ranjan <darsh.ranjan@here.com>
Url: https://github.com/dranjan/python-plyfile

%description
Python module, which provides a simple facility for reading and writing ASCII and binary PLY files.

%prep
%setup -n %{name}-%{unmangled_version} -n %{name}-%{unmangled_version}

%build
env CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --prefix=${RPM_BUILD_ROOT}%{cat_prefix} --install-data=${RPM_BUILD_ROOT}%{_datadir} --single-version-externally-managed --record=/dev/null

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
/
