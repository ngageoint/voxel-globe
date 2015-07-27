%include %{_sourcedir}/common.inc

Name:     bokeh 
Version:  0.9.1
Release:  1%{?dist}
Summary:  Statistical and novel interactive HTML plots for Python
Source:   %{name}-%{version}.tar.gz
Source1:  common.inc

License:  New BSD
Group:    Development/Libraries
URL:      https://pypi.python.org/pypi/bokeh
BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildRequires: python
BuildArch: noarch

%description
Bokeh is a Python interactive visualization library that targets modern web browsers for presentation. Its goal is to provide elegant, concise construction of novel graphics in the style of D3.js, but also deliver this capability with high-performance interactivity over very large or streaming datasets. Bokeh can help anyone who would like to quickly and easily create interactive plots, dashboards, and data applications.

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
