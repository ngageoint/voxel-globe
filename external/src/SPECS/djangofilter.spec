%include %{_sourcedir}/common.inc

Name:     django-filter
Version:  0.9.2
Release:  1%{?dist}
Summary:  Django-filter is a reusable Django application for allowing users to filter querysets dynamically
Source:   %{name}-%{version}.tar.gz
Source1:  common.inc

License:  BSD
Group:    Development/Languages
URL:      https://pypi.python.org/pypi/django-filter
BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildArch: noarch
BuildRequires: python-devel,python-setuptools,django

%description
Django-filter is a generic, reusable application to alleviate writing some of 
the more mundane bits of view code. Specifically, it allows users to filter 
down a queryset based on a model’s fields, displaying the form to let them do 
this.Django-filter is a generic, reusable application to alleviate writing 
some of the more mundane bits of view code. Specifically, it allows users to 
filter down a queryset based on a model’s fields, displaying the form to let
them do this.

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

