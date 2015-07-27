%include %{_sourcedir}/common.inc

Name:     pytools
Version:  2014.3.5
Release:  1%{?dist}
Summary:  A collection of tools for Python
Source:   %{name}-%{version}.tar.gz
Source1:  common.inc

License:  MIT
Group:    Development/Libraries
URL:      https://pypi.python.org/pypi/pytools
BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildRequires: python
BuildArch:  noarch

%description
Pytools is a big bag of things that are “missing” from the Python standard
library. This is mainly a dependency of my other software packages, and is probably of little interest to you unless you use those. If you’re curious nonetheless, here’s what’s on offer:

A ton of small tool functions such as len_iterable, argmin, tuple generation, permutation generation, ASCII table pretty printing, GvR’s mokeypatch_xxx() hack, the elusive flatten, and much more.
Michele Simionato’s decorator module
A time-series logging module, pytools.log.
Batch job submission, pytools.batchjob.
A lexer, pytools.lex.

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
