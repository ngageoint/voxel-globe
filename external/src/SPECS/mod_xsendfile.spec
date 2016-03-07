%include %{_sourcedir}/common.inc

Name:   mod_xsendfile
Version:  0.12
Release:  1%{?dist}
Summary:  Apache2 module that processes X-SENDFILE headers
Source:   https://github.com/nmaier/mod_xsendfile/archive/0.12/%{name}-%{version}.tar.gz
Source1:        common.inc

License:  ASL 2.0
Group:    System Environment/Libraries
URL:    http://tn123.ath.cx/mod_xsendfile/
BuildRoot:  %{_tmppath}/%{name}-%{version}-root
BuildRequires:  httpd-devel
BuildRequires: apr-devel
Requires: httpd

%description
mod_xsendfile is a small Apache2 module that processes X-SENDFILE headers
registered by the original output handler.

If it encounters the presence of such header it will discard all output and
send the file specified by that header instead using Apache internals
including all optimizations like caching-headers and sendfile or mmap if
configured.

It is useful for processing script-output of e.g. php, perl or any cgi.

%prep
%setup

%{__cat} <<EOF >mod_xsendfile.conf
### Load the module
LoadModule xsendfile_module         modules/mod_xsendfile.so

### Enables or disables header processing, default is disabled
XSendFile on

EOF

%build
apxs -c mod_xsendfile.c

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%{__install} -Dp -m0755 .libs/mod_xsendfile.so %{buildroot}%{_libdir}/httpd/modules/mod_xsendfile.so
%{__install} -Dp -m0644 mod_xsendfile.conf %{buildroot}%{_sysconfdir}/httpd/conf.d/mod_xsendfile.conf

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-, root, root, 0755)
%doc docs/Readme.html
%config(noreplace) %{_sysconfdir}/httpd/conf.d/mod_xsendfile.conf
%{_libdir}/httpd/modules/mod_xsendfile.so

%changelog
* Fri Feb 19 2016 Andrew Neff <andrew.neff@visionsystemsinc.com>
- Back port to version 0.12

* Thu Apr 25 2013 Yukinari Toyota <xxseyxx@gmail.com> - 1.0b1
- Initial spec file creation.