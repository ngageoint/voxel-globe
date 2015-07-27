%include %{_sourcedir}/common.inc

Name:		billiard
Version:	3.3.0.20
Release:	1%{?dist}
Summary:	Fork of the Python multiprocessing package
Source:		%{name}-%{version}.tar.gz
Source1:        common.inc

License:	BSD
Group:		Development/Languages
URL: 		http://pypi.python.org/pypi/%{name}
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root
BuildRequires:  python-devel
Requires:       python, setuptools

%description
billiard is a fork of the Python 2.7 multiprocessing package. The multiprocessing package itself is a renamed and updated version of R Oudkerk's pyprocessing package. This standalone variant is intended to be compatible with Python 2.4 and 2.5, and will draw it's fixes/improvements from python-trunk.
-This package would not be possible if not for the contributions of not only the current maintainers but all of the contributors to the original pyprocessing package listed here
-Also it is a fork of the multiprocessin backport package by Christian Heims.
-It includes the no-execv patch contributed by R. Oudkerk.
-And the Pool improvements previously located in Celery.

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
%exclude /usr/lib/debug
/

