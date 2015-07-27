%include %{_sourcedir}/common.inc

Name:	   	utm
Version:  0.4.0
Release:  1%{?dist}
Summary:  Utm conversion library
Source:   %{name}-%{version}.tar.gz
Source1:  common.inc

License:  Tobias Bieniek License
Group:    Development/Libraries
URL:      https://pypi.python.org/pypi/utm
BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildRequires: python
Requires: python
BuildArch: noarch

%description
Bidirectional UTM-WGS84 converter for python

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

