%include %{_sourcedir}/common.inc

Name:	   	Pygments
Version:  2.0.2
Release:  1%{?dist}
Summary:  Pygments is a syntax highlighting package written in Python
Source:   %{name}-%{version}.tar.gz
Source1:  common.inc

License:  BSD
Group:    Development/Libraries
URL:      https://pypi.python.org/pypi/Pygments
BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildRequires: python
Requires: python
BuildArch: noarch

%description
Pygments is a syntax highlighting package written in Python.

It is a generic syntax highlighter suitable for use in code hosting, forums,
wikis or other applications that need to prettify source code. Highlights
are:
- a wide range of over 300 languages and other text formats is supported
- special attention is paid to details, increasing quality by a fair amount
- support for new languages and formats are added easily
- a number of output formats, presently HTML, LaTeX, RTF, SVG, all image formats that PIL supports and ANSI sequences
- it is usable as a command-line tool and as a library

%prep
%setup -q -n %{name}-%{version}

%build
env CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --prefix=${RPM_BUILD_ROOT}%{cat_prefix} --install-data=${RPM_BUILD_ROOT}%{_datadir} --single-version-externally-managed --record=/dev/null

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
/

