%include %{_sourcedir}/common.inc

Summary: Enhanced interactive Python shell
Name: ipython
Version: 3.1.0
Release:	1%{?dist}
License: BSD
Group: Development/Libraries
URL: http://ipython.scipy.org/

Packager: Dag Wieers <dag@wieers.com>
Vendor: Dag Apt Repository, http://dag.wieers.com/apt/

Source: http://ipython.scipy.org/dist/ipython-%{version}.tar.gz
Source1:        common.inc

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

BuildArch: noarch

%description
IPython provides a replacement for the interactive Python interpreter with
extra functionality.

%prep
%setup

%build
%{__python} setup.py build

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --prefix=${RPM_BUILD_ROOT}%{cat_prefix} --install-data=${RPM_BUILD_ROOT}%{cat_prefix}
#WHY is there no /share in the install-data?! I don't know, ASK ipython! I'm sure it's a "bug" in the setup.py somewhere

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-, root, root, 0755)
%doc COPYING.rst README.rst examples
%{_bindir}/ip*
%{python_sitelib}/IPython/
%{python_sitelib}/ipython*.egg-info
%{_mandir}/man1/ip*

%changelog
* Mon May 29 2006 Dag Wieers <dag@wieers.com> - 0.7.1.fix1-1
- Initial package. (using DAR)
