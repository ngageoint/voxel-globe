%include %{_sourcedir}/common.inc

Name:		  requests
Version:	2.7.0
Release:	1%{?dist}
Summary:	Python HTTP for Humans
Source:		%{name}-%{version}.tar.gz
Source1:  common.inc

License:	Apache2
Group:		Development/Libraries
URL:      https://pypi.python.org/pypi/requests
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root
BuildRequires:  python
Requires:       python
BuildArch: 	noarch

%description
Requests is an Apache2 Licensed HTTP library, written in Python, for human beings.

Most existing Python modules for sending HTTP requests are extremely verbose and cumbersome. Python’s builtin urllib2 module provides most of the HTTP capabilities you should need, but the api is thoroughly broken. It requires an enormous amount of work (even method overrides) to perform the simplest of tasks.

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

