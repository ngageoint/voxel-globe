%include %{_sourcedir}/common.inc

Name:     pandas
Version:  0.16.1
Release:  1%{?dist}
Summary:  Powerful data structures for data analysis, time series,and statistics
Source:   %{name}-%{version}.tar.gz
Source1:  common.inc

License:  BSD
Group:    Development/Libraries
URL:      https://pypi.python.org/pypi/pandas
BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildRequires: python

%description
pandas is a Python package providing fast, flexible, and expressive data structures designed to make working with structured
(tabular, multidimensional, potentially heterogeneous) and time series data both easy and intuitive. It aims to be the 
fundamental high-level building block for doing practical, real world data analysis in Python. Additionally, it has the
broader goal of becoming the most powerful and flexible open source data analysis / manipulation tool available in any
language. It is already well on its way toward this goal.

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
