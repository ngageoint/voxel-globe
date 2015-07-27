%include %{_sourcedir}/common.inc

Name:		Flask
Version:	0.10.1
Release:	1%{?dist}
Summary:	A microframework based on Werkzeug, Jinja2 and good intentions
Source:		%{name}-%{version}.tar.gz
Source1:    common.inc

License:	BSD
Group:		Development/Libraries
URL: 		https://pypi.python.org/pypi/flask
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root
BuildRequires:  python
BuildArch: noarch

%description
Flask is a microframework for Python based on Werkzeug, Jinja 2 and good intentions. And before you ask: It’s BSD licensed!

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
