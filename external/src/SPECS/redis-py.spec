%include %{_sourcedir}/common.inc

Name:		redis-py
Version:	2.10.3
Release:	1%{?dist}
Summary:	Python client for Redis key-value store
Source:		%{name}-%{version}.tar.gz
Source1:    common.inc

License:	BSD
Group:		Development/Libraries
URL: 		https://pypi.python.org/pypi/redis
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root
BuildRequires:  python
BuildArch: noarch

%description
Python client for Redis key-value store

The Python interface to the Redis key-value store.

%prep
%setup -q -n redis-%{version}

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
