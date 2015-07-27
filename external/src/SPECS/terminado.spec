%include %{_sourcedir}/common.inc

Summary: Terminals served to term.js using Tornado websockets
Name:    terminado
Version: 0.5
Release: 1%{?dist}
License: BSD
Group:   Development/Libraries
URL:     https://pypi.python.org/pypi/terminado

Source:  https://pypi.python.org/packages/source/t/%{name}/%{name}-%{version}.tar.gz
Source1: common.inc

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildArch: noarch

%description
This is a Tornado websocket backend for the term.js Javascript terminal emulator library.

It evolved out of pyxterm, which was part of GraphTerm (as lineterm.py), v0.57.0 (2014-07-18), and ultimately derived from the public-domain Ajaxterm code, v0.11 (2008-11-13) (also on Github as part of QWeb).

%prep
%setup

%build
%{__python} setup.py build

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --prefix=${RPM_BUILD_ROOT}%{cat_prefix} --install-data=${RPM_BUILD_ROOT}%{cat_prefix} --record=/dev/null
#WHY is there no /share in the install-data?! I don't know, ASK ipython! I'm sure it's a "bug" in the setup.py somewhere

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-, root, root, 0755)
/

%changelog
* Wed May 6 2015 Andy Neff <andrew.neff@visionsystemsinc.com>
- Initial package.