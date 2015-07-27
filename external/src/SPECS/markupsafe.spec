%include %{_sourcedir}/common.inc

Name:		MarkupSafe
Version:	0.23
Release:	1%{?dist}
Summary:	Implements a XML/HTML/XHTML Markup safe string for Python
Source:		%{name}-%{version}.tar.gz
Source1:        common.inc

License:	BSD
Group:		Development/Libraries
URL: 		http://pypi.python.org/pypi/%{name}
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root
BuildRequires:  python-devel
Requires:       python

%description
Implements a unicode subclass that supports HTML strings

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
%exclude /usr/lib/debug
/

