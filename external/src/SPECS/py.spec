%include %{_sourcedir}/common.inc

Name:     py
Version:  1.4.27
Release:  1%{?dist}
Summary:  library with cross-python path, ini-parsing, io, code, log facilities
Source:   %{name}-%{version}.tar.gz
Source1:  common.inc

License:  MIT
Group:    Development/Libraries
URL:      https://pypi.python.org/pypi/py
BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildRequires: python
BuildArch:  noarch

%description
The py lib is a Python development support library featuring the following tools and modules:
-py.path: uniform local and svn path objects
-py.apipkg: explicit API control and lazy-importing
-py.iniconfig: easy parsing of .ini files
-py.code: dynamic code generation and introspection

%prep
%setup -q -n %{name}-%{version}

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
