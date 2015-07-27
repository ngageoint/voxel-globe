%include %{_sourcedir}/common.inc

Name:		winpdb
Version:	1.4.8
Release:	1%{?dist}
Summary:	Graphical Multiprocess Python debugger
Source:		%{name}-%{version}.tar.gz
Source1:        common.inc

License:	GPL
Group:		Development/Libraries
URL: 		http://winpdb.org/
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root
BuildRequires:  python
Requires:       python
BuildArch: 	noarch

%description
Winpdb is a platform independent GPL Python debugger with support for multiple threads, namespace modification, embedded debugging, encrypted communication and is up to 20 times faster than pdb

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

