%include %{_sourcedir}/common.inc

Name:     greenlet
Version:	0.4.7
Release:	1%{?dist}
Summary:	Lightweight in-process concurrent programming
Source:		%{name}-%{version}.zip
Source1:        common.inc

License:	MIT
Group:		Development/Libraries
URL: 		https://pypi.python.org/pypi/greenlet
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root
BuildRequires:  python

%description
The greenlet package is a spin-off of Stackless, a version of CPython that supports micro-threads called “tasklets”. Tasklets run pseudo-concurrently (typically in a single or a few OS-level threads) and are synchronized with data exchanges on “channels”.

A “greenlet”, on the other hand, is a still more primitive notion of micro-thread with no implicit scheduling; coroutines, in other words. This is useful when you want to control exactly when your code runs. You can build custom scheduled micro-threads on top of greenlet; however, it seems that greenlets are useful on their own as a way to make advanced control flow structures. For example, we can recreate generators; the difference with Python’s own generators is that our generators can call nested functions and the nested functions can yield values too. Additionally, you don’t need a “yield” keyword. See the example in tests/test_generator.py.

Greenlets are provided as a C extension module for the regular unmodified interpreter.

Greenlets are lightweight coroutines for in-process concurrent programming.

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
