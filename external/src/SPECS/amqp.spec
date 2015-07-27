%include %{_sourcedir}/common.inc

Name:		amqp
Version:	1.4.6
Release:	1%{?dist}
Summary:	Client library for AMQP
Source:		%{name}-%{version}.tar.gz
Source1:        common.inc

License:	LGPLv2+
Group:		Development/Languages
URL: 		http://pypi.python.org/pypi/amqp
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root
BuildRequires:  python-devel
Requires:       python, setuptools
Packager:	Yury V. Zaytsev <yury@shurup.com>
Vendor:		Dag Apt Repository, http://dag.wieers.com/apt/
BuildArch: 	noarch

%description
Client library for AMQP (Advanced Message Queuing Protocol)

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

