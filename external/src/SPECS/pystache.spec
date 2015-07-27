%include %{_sourcedir}/common.inc

Name:		pystache
Version:	0.5.4
Release:	1%{?dist}
Summary:	Mustache for Python
Source:		%{name}-%{version}.tar.gz
Source1:    common.inc

License:	MIT
Group:		Development/Libraries
URL: 		https://pypi.python.org/pypi/pystache
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root
BuildRequires:  python
BuildArch: noarch

%description
Inspired by ctemplate and et, Mustache is a framework-agnostic way to render logic-free views.

As ctemplates says, "It emphasizes separating logic from presentation: it is impossible to embed application logic in this template language."

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
