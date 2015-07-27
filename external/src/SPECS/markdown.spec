%include %{_sourcedir}/common.inc

Name:		Markdown
Version:	2.6.2
Release:	1%{?dist}
Summary:	Python implementation of Markdown
Source:		%{name}-%{version}.tar.gz
Source1:    common.inc

License:	BSD
Group:		Development/Libraries
URL: 		https://pypi.python.org/pypi/markdown
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root
BuildRequires:  python
BuildArch: noarch

%description
This is a Python implementation of John Gruber’s Markdown. It is almost completely compliant with the reference implementation, though there are a few known issues. See Features for information on what exactly is supported and what is not. Additional features are supported by the Available Extensions.

%prep
%setup -q -n %{name}-%{version}

%build
env CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --prefix=${RPM_BUILD_ROOT}%{cat_prefix} --install-data=${RPM_BUILD_ROOT}%{_datadir}

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
/
