%include %{_sourcedir}/common.inc

Name:     sphinx_rtd_theme
Version:  0.1.8
Release:  1%{?dist}
Summary:  ReadTheDocs.org theme for Sphinx, 2013 version
Source:   %{name}-%{version}.tar.gz
Source1:  common.inc

License:  MIT
Group:    Development/Libraries
URL:      https://pypi.python.org/pypi/sphinx_rtd_theme
BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildRequires: python
BuildArch: noarch

%description
ReadTheDocs.org theme for Sphinx, 2013 version

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
