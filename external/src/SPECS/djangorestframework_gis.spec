%include %{_sourcedir}/common.inc

Name:		djangorestframework-gis
Version:	0.8.2
Release:	1%{?dist}
Summary:	Geographic add-ons for Django Rest Framework
Source:		%{name}-%{version}.tar.gz
Source1:        common.inc

License:	BSD
Group:		Development/Languages
URL: 		https://pypi.python.org/pypi/djangorestframework-gis
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root
BuildArch:      noarch
BuildRequires:  python-devel,python-setuptools,django

%description
Geographic add-ons for Django Rest Framework

%prep
%setup -q -n %{name}-%{version}

%build
env CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --single-version-externally-managed --record=/dev/null --prefix=${RPM_BUILD_ROOT}%{cat_prefix} --install-data=${RPM_BUILD_ROOT}%{_datadir}

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%doc LICENSE README.rst
%{python_sitelib}

%post

%postun

#%changelog
