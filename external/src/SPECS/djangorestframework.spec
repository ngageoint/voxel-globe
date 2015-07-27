%include %{_sourcedir}/common.inc

Name:		djangorestframework
Version:	3.1.1
Release:	1%{?dist}
Summary:	Web APIs for Django, made easy.
Source:		%{name}-%{version}.tar.gz
Source1:        common.inc

License:	BSD
Group:		Development/Languages
URL: 		https://pypi.python.org/pypi/djangorestframework
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root
BuildArch:      noarch
BuildRequires:  python-devel,python-setuptools,django

%description
Django REST framework is a powerful and flexible toolkit that makes it easy to build Web APIs.
Some reasons you might want to use REST framework:
-The Web browsable API is a huge usability win for your developers.
-Authentication policies including OAuth1a and OAuth2 out of the box.
-Serialization that supports both ORM and non-ORM data sources.
-Customizable all the way down - just use regular function-based views if you don't need the more powerful features.
-Extensive documentation, and great community support.
-Used and trusted by large companies such as Mozilla and Eventbrite.

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
%{python_sitelib}

%post

%postun

#%changelog

