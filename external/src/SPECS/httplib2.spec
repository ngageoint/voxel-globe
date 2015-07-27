%include %{_sourcedir}/common.inc

Name:		httplib2
Version:	0.9.1
Release:	1%{?dist}
Summary:	A comprehensive HTTP client library.
Source:		%{name}-%{version}.tar.gz
Source1:    common.inc

License:	MIT
Group:		Development/Libraries
URL: 		https://pypi.python.org/pypi/httplib2
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root
BuildRequires:  python
BuildArch: noarch

%description
A comprehensive HTTP client library, httplib2 supports many features left out of other HTTP libraries.

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
