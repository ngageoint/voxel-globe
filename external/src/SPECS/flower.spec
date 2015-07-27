%include %{_sourcedir}/common.inc

Name:		flower
Version:	0.8.2
Release:	1%{?dist}
Summary:	Celery web monitor
Source:		%{name}-%{version}.tar.gz
Source1:        common.inc

License:	New BSD
Group:		Development/Languages
URL: 		http://pypi.python.org/pypi/%{name}
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root
BuildRequires:  python-devel
Requires:       python, setuptools
BuildArch: 	noarch

%description
Flower is a web based tool for monitoring and administrating Celery clusters.

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

