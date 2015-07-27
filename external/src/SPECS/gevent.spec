%include %{_sourcedir}/common.inc

Name:		gevent
Version:	1.0.2
Release:	1%{?dist}
Summary:	Coroutine-based network library
Source:		%{name}-%{version}.tar.gz
Source1:    common.inc

License:	MIT
Group:		Development/Libraries
URL: 		https://pypi.python.org/pypi/gevent
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root
BuildRequires:  python

%description
gevent is a coroutine-based Python networking library.

Features include:
-Fast event loop based on libev.
-Lightweight execution units based on greenlet.
-Familiar API that re-uses concepts from the Python standard library.
-Cooperative sockets with SSL support.
-DNS queries performed through c-ares or a threadpool.
-Ability to use standard library and 3rd party modules written for standard blocking sockets

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
