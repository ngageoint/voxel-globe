%include %{_sourcedir}/common.inc

Name:     django-model-utils
Version:  2.2
Release:  1%{?dist}
Summary:  Django model mixins and utilities
Source:   %{name}-%{version}.tar.gz
Source1:  common.inc

License:  BSD
Group:    Development/Libraries
URL:      https://pypi.python.org/pypi/%{name}
BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildRequires: python
BuildArch:  noarch

%description
Django model mixins and utilities.

django-model-utils supports Django 1.4.10 and later on Python 2.6, 2.7, 3.2, 3.3 and 3.4.

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
