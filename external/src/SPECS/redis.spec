%include %{_sourcedir}/common.inc

Name:		redis
Version:	3.0.1
Release:	1%{?dist}
Summary:	Redis advanced key-value cache and store.
Source:		%{name}-%{version}.tar.gz
Source1:        common.inc

License:	BSD
Group:		Development/Library
URL: 		  http://redis.io/
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root

%description
Redis is an open source, BSD licensed, advanced key-value cache and store. It is often referred to as a data structure server since keys can contain strings, hashes, lists, sets, sorted sets, bitmaps and hyperloglogs.

%prep
%setup -q -n %{name}-%{version}

%build
make %{_smp_mflags}

%check
make test

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
make install PREFIX="%{buildroot}"

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%exclude /usr/lib/debug
%{_bindir}

