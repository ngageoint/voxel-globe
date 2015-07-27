%include %{_sourcedir}/common.inc

Name:	   	pexpect
Version:  3.3
Release:  1%{?dist}
Summary:  Pexpect allows easy control of interactive console applications
Source:   %{name}-%{version}.tar.gz
Source1:  common.inc

License:  ISC License
Group:    Development/Libraries
URL:      https://pypi.python.org/pypi/pexpect
BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildRequires: python
Requires: python
BuildArch: noarch

%description
Pexpect is a pure Python module for spawning child applications; controlling them; and responding to expected patterns in their output. Pexpect works like Don Libes’ Expect. Pexpect allows your script to spawn a child application and control it as if a human were typing commands.

Pexpect can be used for automating interactive applications such as ssh, ftp, passwd, telnet, etc. It can be used to a automate setup scripts for duplicating software package installations on different servers. It can be used for automated software testing. Pexpect is in the spirit of Don Libes’ Expect, but Pexpect is pure Python. Unlike other Expect-like modules for Python, Pexpect does not require TCL or Expect nor does it require C extensions to be compiled. It should work on any platform that supports the standard Python pty module. The Pexpect interface was designed to be easy to use.

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

