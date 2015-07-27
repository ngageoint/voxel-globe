%include %{_sourcedir}/common.inc

Name:    jsonschema
Version: 2.4.0
Release: 1%{?dist}
Summary: An implementation of JSON Schema validation for Python
License: MIT
Group:   Development/Libraries
URL:     https://pypi.python.org/pypi/jsonschema

Source:  https://pypi.python.org/packages/source/j/%{name}/%{name}-%{version}.tar.gz
Source1: common.inc

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildArch: noarch

%description
jsonschema is an implementation of JSON Schema for Python (supporting 2.6+ including Python 3).

%prep
%setup

%build
%{__python} setup.py build

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --prefix=${RPM_BUILD_ROOT}%{cat_prefix} --install-data=${RPM_BUILD_ROOT}%{_datadir} --single-version-externally-managed --record=/dev/null
#WHY is there no /share in the install-data?! I don't know, ASK ipython! I'm sure it's a "bug" in the setup.py somewhere

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-, root, root, 0755)
/

%changelog
* Wed May 6 2015 Andy Neff <andrew.neff@visionsystemsinc.com>
- Initial package.
