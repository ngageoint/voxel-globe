%include %{_sourcedir}/common.inc

Name:		tifffile
Version:	2014.10.10.1
Release:	1%{?dist}
Summary:	Python Tifffile reader
Source:		https://github.com/andyneff/tifffile/archive/%{name}-%{version}.tar.gz
Source1:    common.inc

License:	BSD
Group:		Development/Libraries
URL: 		http://www.lfd.uci.edu/~gohlke/
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root
Vendor:     Christoph Gohlke <cgohlke@uci.edu>
Requires:   python

%description
Python Tifffile reader

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
%exclude /usr/lib/debug
/

