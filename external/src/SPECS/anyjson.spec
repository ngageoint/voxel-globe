%include %{_sourcedir}/common.inc

Name:		anyjson
Version:	0.3.3
Release:	1%{?dist}
Summary:	Wraps the best available JSON implementation available
Source:		%{name}-%{version}.tar.gz
Source1:        common.inc

License:	BSD
Group:		Development/Languages
URL: 		http://pypi.python.org/pypi/anyjson
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root
BuildRequires:  python-devel
Requires:       python, setuptools
Packager:	Yury V. Zaytsev <yury@shurup.com>
Vendor:		Dag Apt Repository, http://dag.wieers.com/apt/
BuildArch: 	noarch

%description
Anyjson loads whichever is the fastest JSON module installed and provides a uniform API regardless of which JSON implementation is used.

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

