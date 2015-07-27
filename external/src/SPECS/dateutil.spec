%include %{_sourcedir}/common.inc

Name:		dateutil
Version:	2.4.2
Release:	1%{?dist}
Summary:	Powerful extensions to the standard datetime module
Source:		python-%{name}-%{version}.tar.gz
Source1:        common.inc

License:	Python
Group:		Development/Languages
URL: 		http://labix.org/python-dateutil
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root
BuildArch:      noarch
BuildRequires:  python-devel,python-setuptools	

%description
The dateutil module provides powerful extensions to the standard datetime
module available in Python 2.3+.

%prep
%setup -q -n python-%{name}-%{version}

iconv -f ISO-8859-1 -t utf8 NEWS > NEWS.utf8 && \
  touch -r NEWS NEWS.utf8 && \
  mv NEWS.utf8 NEWS

%build
env CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build

%check
env PYTHONPATH=${RPM_BUILD_ROOT}%{python_sitelib} %{__python} dateutil/test/test.py

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --single-version-externally-managed --record=/dev/null --prefix=${RPM_BUILD_ROOT}%{cat_prefix} --install-data=${RPM_BUILD_ROOT}%{_datadir}

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%doc LICENSE NEWS README.rst
%{python_sitelib}/dateutil/
%{python_sitelib}/*.egg-info

%post

%postun

#%changelog

