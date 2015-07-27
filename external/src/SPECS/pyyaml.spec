%include %{_sourcedir}/common.inc

Name:		PyYAML
Version:	3.11
Release:	1%{?dist}
Summary:	YAML parser and emitter for Python
Source:		%{name}-%{version}.tar.gz
Source1:        common.inc

License:	MIT
Group:		Development/Libraries
URL:  		https://pypi.python.org/pypi/%{name}
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root
BuildRequires:  python

%description
YAML is a data serialization format designed for human readability and interaction with scripting languages. PyYAML is a YAML parser and emitter for Python.

PyYAML features a complete YAML 1.1 parser, Unicode support, pickle support, capable extension API, and sensible error messages. PyYAML supports standard YAML tags and provides Python-specific tags that allow to represent an arbitrary Python object.

PyYAML is applicable for a broad range of tasks from complex configuration files to object serialization and persistance.

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
