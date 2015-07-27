%include %{_sourcedir}/common.inc

Name:		certifi
Version:	2015.04.28
Release:	1%{?dist}
Summary:	Python package for providing Mozilla's CA Bundle
Source:		%{name}-%{version}.tar.gz
Source1:        common.inc

License:	ISC
Group:		Development/Languages
URL: 		https://pypi.python.org/pypi/certifi
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root
BuildArch:      noarch
BuildRequires:  python

%description
This installable Python package contains a CA Bundle that you can reference in
 your Python code. This is useful for verifying HTTP requests, for example.

This is the same CA Bundle which ships with the Requests codebase, and is
derived from Mozilla Firefox's canonical set.

%prep
%setup -q -n %{name}-%{version}

%build
env CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --single-version-externally-managed --record=/dev/null --prefix=${RPM_BUILD_ROOT}%{cat_prefix} --install-data=${RPM_BUILD_ROOT}%{_datadir}

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%{python_sitelib}

%post

%postun

#%changelog

