%include %{_sourcedir}/common.inc

Name:		itsdangerous
Version:	0.24
Release:	1%{?dist}
Summary:	Various helpers to pass trusted data to untrusted environments and back
Source:		%{name}-%{version}.tar.gz
Source1:    common.inc

License:	BSD
Group:		Development/Libraries
URL: 		https://pypi.python.org/pypi/itsdangerous
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root
Requires:   python

%description
It’s Dangerous
  ... so better sign this
Various helpers to pass data to untrusted environments and to get it back safe and sound.

This repository provides a module that is a port of the django signing module. It’s not directly copied but some changes were applied to make it work better on its own.

Also I plan to add some extra things. Work in progress.

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
