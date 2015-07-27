%include %{_sourcedir}/common.inc

Name:     pytz
Version:  2015.2
Release:  1%{?dist}
Summary:  World Timezone Definitions for Python
Source:   %{name}-%{version}.tar.bz2
Source1:  common.inc

License:  MIT
Group:    Development/Languages
URL:      https://pypi.python.org/pypi/pytz
BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildArch: noarch
BuildRequires: python-devel
#Requires:       tzdata

%description
pytz brings the Olson tz database into Python. This library allows accurate
and cross platform timezone calculations using Python 2.3 or higher. It
also solves the issue of ambiguous times at the end of daylight savings,
which you can read more about in the Python Library Reference
(datetime.tzinfo).

Amost all (over 540) of the Olson timezones are supported.

%prep
%setup -q

%build
env CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --single-version-externally-managed -O1 --record=/dev/null --prefix=${RPM_BUILD_ROOT}%{cat_prefix} --install-data=${RPM_BUILD_ROOT}%{_datadir}
chmod +x $RPM_BUILD_ROOT%{python_sitelib}/pytz/*.py
#rm -rf  $RPM_BUILD_ROOT%{python_sitelib}/pytz/zoneinfo

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc CHANGES.txt LICENSE.txt README.txt
%{python_sitelib}/pytz/
%{python_sitelib}/*.egg-info

%post

%postun

#%changelog

