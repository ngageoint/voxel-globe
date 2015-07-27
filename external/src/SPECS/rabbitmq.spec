%include %{_sourcedir}/common.inc

Name:     rabbitmq-server
Version:  3.5.3
Release:  1%{?dist}
Summary:  The RabbitMQ server
Source:   %{name}-%{version}.tar.gz
Source1:  rabbitmq-server.init
Source2:  rabbitmq-script-wrapper
Source3:  rabbitmq-server.logrotate
Source4:  rabbitmq-server.ocf
Source5:  common.inc
License:	MPLv1.1 and MIT and ASL 2.0 and BSD
Group:		Development/Library
URL:      http://www.rabbitmq.com/
BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildArch: noarch
BuildRequires: erlang >= R13B-03, python-simplejson, xmlto, libxslt
Requires:	erlang >= R13B-03, logrotate
#Requires(post):	chkconfig initscripts
#Requires(pre):	chkconfig initscripts

# We want to install into /usr/lib, even on 64-bit platforms
%define _rabbit_libdir %{_exec_prefix}/lib/rabbitmq
%define _rabbit_erllibdir %{_rabbit_libdir}
#/lib/rabbitmq_server-%{version}
%define _rabbit_wrapper %{_builddir}/`basename %{S:2}`
%define _rabbit_server_ocf %{_builddir}/`basename %{S:4}`
%define _plugins_state_dir %{_localstatedir}/lib/rabbitmq/plugins
%define _maindir %{buildroot}%{_rabbit_erllibdir}

%description
RabbitMQ is an implementation of AMQP, the emerging standard for high
performance enterprise messaging. The RabbitMQ server is a robust and
scalable implementation of an AMQP broker.

%prep
%setup -q -n %{name}-%{version}

sed -i 's|^#!/bin/sh -e|#!/usr/bin/env bash|' scripts/rabbitmqctl
sed -i -r 's|(SYS_PREFIX=)|\1$(cd $(dirname $(readlink -f ${BASH_SOURCE[0]}))/../%{prefix_lib_rel}; pwd)|' scripts/rabbitmq-defaults
sed -i -r 's|/etc|%{_sysconfdir}|' scripts/rabbitmq-defaults
sed -i -r 's|/var|%{_localstatedir}|' scripts/rabbitmq-defaults

%build
cp %{S:2} %{_rabbit_wrapper}
cp %{S:4} %{_rabbit_server_ocf}
make %{?_smp_mflags}

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

# Note that we pass /tmp to DOC_INSTALL_DIR here because we're using %doc
# to actually install rabbitmq.config.example, so this is just a fake/temp path
make install TARGET_DIR=%{_maindir} \
             SBIN_DIR=%{buildroot}%{_rabbit_libdir}/bin \
             MAN_DIR=%{buildroot}%{_mandir} \
             DOC_INSTALL_DIR=%{buildroot}/delme/

rm -rf %{buildroot}/delme/
mkdir -p %{buildroot}%{_localstatedir}/lib/rabbitmq/mnesia
mkdir -p %{buildroot}%{_localstatedir}/log/rabbitmq

#Copy all necessary lib files etc.
install -p -D -m 0755 %{S:1} %{buildroot}%{_initrddir}/rabbitmq-server
install -p -D -m 0755 %{_rabbit_wrapper} %{buildroot}%{_bindir}/rabbitmqctl
install -p -D -m 0755 %{_rabbit_wrapper} %{buildroot}%{_bindir}/rabbitmq-server
install -p -D -m 0755 %{_rabbit_wrapper} %{buildroot}%{_bindir}/rabbitmq-plugins
install -p -D -m 0755 %{_rabbit_server_ocf} %{buildroot}%{_exec_prefix}/lib/ocf/resource.d/rabbitmq/rabbitmq-server

install -p -D -m 0644 %{S:3} %{buildroot}%{_sysconfdir}/logrotate.d/rabbitmq-server

mkdir -p %{buildroot}%{_sysconfdir}/rabbitmq

rm %{_maindir}/LICENSE %{_maindir}/LICENSE-MPL-RabbitMQ %{_maindir}/INSTALL

#Build the list of files
echo '%defattr(-,root,root, -)' >%{_builddir}/%{name}.files
find %{buildroot} -path %{buildroot}%{_sysconfdir} -prune -o '!' -type d -printf "/%%P\n" >>%{_builddir}/%{name}.files



%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files -f ../%{name}.files
%defattr(-,root,root,-)
%attr(0755, rabbitmq, rabbitmq) %dir %{_localstatedir}/lib/rabbitmq
%attr(0755, rabbitmq, rabbitmq) %dir %{_localstatedir}/log/rabbitmq
%dir %{_sysconfdir}/rabbitmq
%{_initrddir}/rabbitmq-server
%config(noreplace) %{_sysconfdir}/logrotate.d/rabbitmq-server
%doc LICENSE*
%doc README
%doc docs/rabbitmq.config.example

%post

%postun

%changelog
* Tue Jun 24 2014 simon@rabbitmq.com 3.3.4-1
- New Upstream Release

* Mon Jun 16 2014 simon@rabbitmq.com 3.3.3-1
- New Upstream Release

* Mon Jun 9 2014 simon@rabbitmq.com 3.3.2-1
- New Upstream Release

* Tue Apr 29 2014 simon@rabbitmq.com 3.3.1-1
- New Upstream Release

* Wed Apr 2 2014 simon@rabbitmq.com 3.3.0-1
- New Upstream Release

* Mon Mar 3 2014 simon@rabbitmq.com 3.2.4-1
- New Upstream Release

* Thu Jan 23 2014 emile@rabbitmq.com 3.2.3-1
- New Upstream Release

* Tue Dec 10 2013 emile@rabbitmq.com 3.2.2-1
- New Upstream Release

* Wed Oct 23 2013 emile@rabbitmq.com 3.2.0-1
- New Upstream Release

* Thu Aug 15 2013 simon@rabbitmq.com 3.1.5-1
- New Upstream Release

* Tue Jun 25 2013 tim@rabbitmq.com 3.1.3-1
- New Upstream Release

* Mon Jun 24 2013 tim@rabbitmq.com 3.1.2-1
- New Upstream Release

* Mon May 20 2013 tim@rabbitmq.com 3.1.1-1
- Test release

* Wed May 1 2013 simon@rabbitmq.com 3.1.0-1
- New Upstream Release

* Tue Dec 11 2012 simon@rabbitmq.com 3.0.1-1
- New Upstream Release

* Fri Nov 16 2012 simon@rabbitmq.com 3.0.0-1
- New Upstream Release

* Fri Dec 16 2011 steve@rabbitmq.com 2.7.1-1
- New Upstream Release

* Tue Nov 8 2011 steve@rabbitmq.com 2.7.0-1
- New Upstream Release

* Fri Sep 9 2011 tim@rabbitmq.com 2.6.1-1
- New Upstream Release

* Fri Aug 26 2011 tim@rabbitmq.com 2.6.0-1
- New Upstream Release

* Mon Jun 27 2011 simon@rabbitmq.com 2.5.1-1
- New Upstream Release

* Thu Jun 9 2011 jerryk@vmware.com 2.5.0-1
- New Upstream Release

* Thu Apr 7 2011 Alexandru Scvortov <alexandru@rabbitmq.com> 2.4.1-1
- New Upstream Release

* Tue Mar 22 2011 Alexandru Scvortov <alexandru@rabbitmq.com> 2.4.0-1
- New Upstream Release

* Thu Feb 3 2011 simon@rabbitmq.com 2.3.1-1
- New Upstream Release

* Tue Feb 1 2011 simon@rabbitmq.com 2.3.0-1
- New Upstream Release

* Mon Nov 29 2010 rob@rabbitmq.com 2.2.0-1
- New Upstream Release

* Tue Oct 19 2010 vlad@rabbitmq.com 2.1.1-1
- New Upstream Release

* Tue Sep 14 2010 marek@rabbitmq.com 2.1.0-1
- New Upstream Release

* Mon Aug 23 2010 mikeb@rabbitmq.com 2.0.0-1
- New Upstream Release

* Wed Jul 14 2010 Emile Joubert <emile@rabbitmq.com> 1.8.1-1
- New Upstream Release

* Tue Jun 15 2010 Matthew Sackman <matthew@rabbitmq.com> 1.8.0-1
- New Upstream Release

* Mon Feb 15 2010 Matthew Sackman <matthew@lshift.net> 1.7.2-1
- New Upstream Release

* Fri Jan 22 2010 Matthew Sackman <matthew@lshift.net> 1.7.1-1
- New Upstream Release

* Mon Oct 5 2009 David Wragg <dpw@lshift.net> 1.7.0-1
- New upstream release

* Wed Jun 17 2009 Matthias Radestock <matthias@lshift.net> 1.6.0-1
- New upstream release

* Tue May 19 2009 Matthias Radestock <matthias@lshift.net> 1.5.5-1
- Maintenance release for the 1.5.x series

* Mon Apr 6 2009 Matthias Radestock <matthias@lshift.net> 1.5.4-1
- Maintenance release for the 1.5.x series

* Tue Feb 24 2009 Tony Garnock-Jones <tonyg@lshift.net> 1.5.3-1
- Maintenance release for the 1.5.x series

* Mon Feb 23 2009 Tony Garnock-Jones <tonyg@lshift.net> 1.5.2-1
- Maintenance release for the 1.5.x series

* Mon Jan 19 2009 Ben Hood <0x6e6562@gmail.com> 1.5.1-1
- Maintenance release for the 1.5.x series

* Wed Dec 17 2008 Matthias Radestock <matthias@lshift.net> 1.5.0-1
- New upstream release

* Thu Jul 24 2008 Tony Garnock-Jones <tonyg@lshift.net> 1.4.0-1
- New upstream release

* Mon Mar 3 2008 Adrien Pierard <adrian@lshift.net> 1.3.0-1
- New upstream release

* Wed Sep 26 2007 Simon MacMullen <simon@lshift.net> 1.2.0-1
- New upstream release

* Wed Aug 29 2007 Simon MacMullen <simon@lshift.net> 1.1.1-1
- New upstream release

* Mon Jul 30 2007 Simon MacMullen <simon@lshift.net> 1.1.0-1.alpha
- New upstream release

* Tue Jun 12 2007 Hubert Plociniczak <hubert@lshift.net> 1.0.0-1.20070607
- Building from source tarball, added starting script, stopping

* Mon May 21 2007 Hubert Plociniczak <hubert@lshift.net> 1.0.0-1.alpha
- Initial build of server library of RabbitMQ package
