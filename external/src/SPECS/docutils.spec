%include %{_sourcedir}/common.inc

Name:     docutils 
Version:  0.12
Release:  1%{?dist}
Summary:  Docutils -- Python Documentation Utilities
Source:   %{name}-%{version}.tar.gz
Source1:  common.inc

License:  BSD/GPL3
Group:    Development/Libraries
URL:      https://pypi.python.org/pypi/docutils
BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildRequires: python
BuildArch: noarch

%description
Docutils is a modular system for processing documentation into useful formats, such as HTML, XML, and LaTeX. For input Docutils supports reStructuredText, an easy-to-read, what-you-see-is-what-you-get plaintext markup syntax

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
