%include %{_sourcedir}/common.inc

Name:		Jinja2
Version:	2.7.3
Release:	1%{?dist}
Summary:	A small but fast and easy to use stand-alone template engine written in pure python.
Source:		%{name}-%{version}.tar.gz
Source1:        common.inc

License:	BSD
Group:		Development/Libraries
URL: 		http://pypi.python.org/pypi/jinja2
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root
BuildRequires:  python-devel
Requires:       python markupsafe
BuildArch: 	noarch

%description
Jinja2 is a template engine written in pure Python. It provides a Django inspired non-XML syntax but supports inline expressions and an optional sandboxed environment.

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

