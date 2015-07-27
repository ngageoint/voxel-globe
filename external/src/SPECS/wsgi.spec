%include %{_sourcedir}/common.inc

Name:		mod_wsgi
Version:	4.4.12
Release:	1%{?dist}
Summary:	A WSGI interface for Python web applications in Apache
Source:		%{name}-%{version}.tar.gz
Source1:        common.inc
Source2:        wsgi.conf

License:	ASL 2.0
Group:		System Environment/Libraries
URL: 		http://modwsgi.org
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root
BuildRequires:  httpd-devel
BuildRequires:  python-devel
Requires: httpd

%description

%prep
%setup -q -n %{name}-%{version}

%build
export CFLAGS="-fno-strict-aliasing"
%configure --with-python=%{_roamdir}/python
make %{?_smp_mflags}

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

make install DESTDIR=$RPM_BUILD_ROOT

install -d -m 755 $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d
install -p -m 644 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d/

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc LICENSE README.rst
%config(noreplace) %{_sysconfdir}/httpd/conf.d/wsgi.conf
%{_libdir}/httpd/modules/mod_wsgi.so

%post

%postun

#%changelog

