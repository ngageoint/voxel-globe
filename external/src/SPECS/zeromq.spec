%include %{_sourcedir}/common.inc

Name:     zeromq
Version:  4.0.5
Release:  1%{?dist}
Summary:  Zero MQ
Source:   %{name}-%{version}.tar.gz
Source1:  common.inc

License:  LGPL
Group:    Development/Library
URL:      http://zeromq.org/
BuildRoot: %{_tmppath}/%{name}-%{version}-root

%description
ØMQ (also spelled ZeroMQ, 0MQ or ZMQ) is a high-performance asynchronous messaging library aimed at use in scalable distributed or concurrent applications. It provides a message queue, but unlike message-oriented middleware, a ØMQ system can run without a dedicated message broker. The library is designed to have a familiar socket-style API.

%prep
%setup -q -n %{name}-%{version}

%build
%configure

make %{_smp_mflags}

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
make install DESTDIR="%{buildroot}"

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%exclude /usr/lib/debug
/

