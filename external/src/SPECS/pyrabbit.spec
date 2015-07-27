%include %{_sourcedir}/common.inc

Name:	   	pyrabbit
Version:  1.1.0
Release:  1%{?dist}
Summary:  A Pythonic interface to the RabbitMQ Management HTTP API
Source:   %{name}-%{version}.tar.gz
Source1:  common.inc

License:  MIT
Group:    Development/Libraries
URL:      https://pypi.python.org/pypi/utm
BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildRequires: python
Requires: python
BuildArch: noarch

%description
There’s no way to easily write programs against RabbitMQs management API without resorting to some messy urllib boilerplate code involving HTTP Basic authentication and parsing the JSON responses, etc. Pyrabbit abstracts this away & provides an intuitive, easy way to work with the data that lives inside of RabbitMQ, and manipulate the resources there

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

