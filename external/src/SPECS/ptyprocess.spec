%include %{_sourcedir}/common.inc

Summary: Run a subprocess in a pseudo terminal
Name:    ptyprocess
Version: 0.4
Release: 1%{?dist}
License: ISCL
Group:   Development/Libraries
URL:     https://pypi.python.org/pypi/ptyprocess

Source:  https://pypi.python.org/packages/source/p/%{name}/%{name}-%{version}.tar.gz
Source1: common.inc

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildArch: noarch

%description
Launch a subprocess in a pseudo terminal (pty), and interact with both the process and its pty.

Sometimes, piping stdin and stdout is not enough. There might be a password prompt that doesn’t read from stdin, output that changes when it’s going to a pipe rather than a terminal, or curses-style interfaces that rely on a terminal. If you need to automate these things, running the process in a pseudo terminal (pty) is the answer.

%prep
%setup

%build
%{__python} setup.py build

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --prefix=${RPM_BUILD_ROOT}%{cat_prefix} --install-data=${RPM_BUILD_ROOT}%{_datadir} --record=/dev/null
#WHY is there no /share in the install-data?! I don't know, ASK ipython! I'm sure it's a "bug" in the setup.py somewhere

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-, root, root, 0755)
/

%changelog
* Wed May 6 2015 Andy Neff <andrew.neff@visionsystemsinc.com>
- Initial package.
