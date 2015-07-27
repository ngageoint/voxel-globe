%include %{_sourcedir}/common.inc

Name:		gevent-websocket
Version:	0.9.5
Release:	1%{?dist}
Summary:	Websocket handler for the gevent pywsgi server, a Python network library
Source:		%{name}-%{version}.tar.gz
Source1:    common.inc

License:	Apache
Group:		Development/Libraries
URL: 		https://pypi.python.org/pypi/gevent-websocket
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root
BuildRequires:  python
BuildArch: noarch

%description
gevent-websocket is a WebSocket library for the gevent networking library.

Features include:
-Integration on both socket level or using an abstract interface.
-RPC and PubSub framework using WAMP (WebSocket Application Messaging Protocol).
-Easily extendible using a simple WebSocket protocol plugin API

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
