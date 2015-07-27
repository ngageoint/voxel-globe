%include %{_sourcedir}/common.inc

Name:		pyparsing
Version:	2.0.3
Release:	1%{?dist}
Summary:	Python parsing module
Source:		%{name}-%{version}.tar.gz
Source1:        common.inc

License:	MIT
Group:		Development/Languages
URL: 		http://pyparsing.wikispaces.com/
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root
BuildArch:      noarch

%description
Python parsing library

%prep
%setup -q

%build
env CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --prefix=${RPM_BUILD_ROOT}%{cat_prefix} --install-data=${RPM_BUILD_ROOT}%{_datadir}


%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
/

%post

%postun

#%changelog

