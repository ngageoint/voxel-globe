%include %{_sourcedir}/common.inc

Name:		  Werkzeug
Version:	0.10.4
Release:	1%{?dist}
Summary:	The Swiss Army knife of Python web development
Source:		%{name}-%{version}.tar.gz
Source1:        common.inc

License:	BSD
Group:		Development/Libraries
URL: 		https://pypi.python.org/pypi/Werkzeug
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root
BuildRequires:  python
Requires:       python
BuildArch: 	noarch

%description
Werkzeug started as simple collection of various utilities for WSGI applications and has become one of the most advanced WSGI utility modules. It includes a powerful debugger, full featured request and response objects, HTTP utilities to handle entity tags, cache control headers, HTTP dates, cookie handling, file uploads, a powerful URL routing system and a bunch of community contributed addon modules.

Werkzeug is unicode aware and doesn’t enforce a specific template engine, database adapter or anything else. It doesn’t even enforce a specific way of handling requests and leaves all that up to the developer. It’s most useful for end user applications which should work on as many server environments as possible (such as blogs, wikis, bulletin boards, etc.).

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

