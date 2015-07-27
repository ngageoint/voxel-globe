%include %{_sourcedir}/common.inc

Name:		pyzmq
Version:	14.6.0
Release:	1%{?dist}
Summary:	Python bindings for 0MQ
Source:		%{name}-%{version}.tar.gz
Source1:        common.inc

License:	LGPL+BSD
Group:		Development/Libraries
URL: 		http://pypi.python.org/pypi/pyzmq
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root
BuildRequires:  python-devel
Requires:       python, zeromq

%description
PyZMQ is the official Python binding for the ZeroMQ Messaging Library 

%prep
%setup -q -n %{name}-%{version}
sed -i 's|from distutils.extension import Extension|from setuptools.extension import Extension|' setup.py
#probably due to upgrading from setuptools 3.6 to 8.0.4 (HUGE JUMP)
%build
env CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py --zmq=%{install_dir}%{cat_prefix} build

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --prefix=${RPM_BUILD_ROOT}%{cat_prefix} --install-data=${RPM_BUILD_ROOT}%{_datadir} --single-version-externally-managed --record=/dev/null

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%exclude /usr/lib/debug
/

