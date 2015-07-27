%include %{_sourcedir}/common.inc

Name:     snowballstemmer 
Version:  1.2.0
Release:  1%{?dist}
Summary:  16 stemmer algorithms
Source:   %{name}-%{version}.tar.gz
Source1:  common.inc

License:  MIT
Group:    Development/Libraries
URL:      https://pypi.python.org/pypi/snowballstemmer
BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildRequires: python
BuildArch: noarch

%description
This package provides 16 stemmer algorithms (15 + Poerter English stemmer) generated from Snowball algorithms

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
