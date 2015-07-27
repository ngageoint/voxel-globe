%include %{_sourcedir}/common.inc

Name:		sympy
Version:	0.7.6
Release:	1%{?dist}
Summary:	Computer algebra system (CAS) in Python
Source:		%{name}-%{version}.tar.gz
Source1:    common.inc

License:	BSD
Group:		Development/Libraries
URL: 		https://pypi.python.org/pypi/sympy
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root
BuildRequires:  python
BuildArch: noarch

%description
SymPy is a Python library for symbolic mathematics. It aims to become a full-featured computer algebra system (CAS) 
while keeping the code as simple as possible in order to be comprehensible and easily extensible. SymPy is written 
entirely in Python and does not require any external libraries, except optionally for plotting support.

%prep
%setup -q -n %{name}-%{version}

%build
env CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --prefix=${RPM_BUILD_ROOT}%{cat_prefix} --install-data=${RPM_BUILD_ROOT}%{cat_prefix}

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
/
