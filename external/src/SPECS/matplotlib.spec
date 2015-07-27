%include %{_sourcedir}/common.inc

Name:		matplotlib
Version:	1.4.3
Release:	1%{?dist}
Summary:	Python plotting library
Source:		%{name}-%{version}.tar.gz
Source1:        common.inc

License:	Python
Group:		Development/Libraries
URL:            http://sourceforge.net/projects/matplotlib/
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root
BuildRequires:  freetype-devel
BuildRequires:  gtk2-devel
BuildRequires:  libpng-devel
BuildRequires:  pygtk2-devel
BuildRequires:  python-dateutil
BuildRequires:  python-devel
BuildRequires:  python-numeric
BuildRequires:  python-tz
BuildRequires:  tkinter
BuildRequires:  tk-devel
BuildRequires:  zlib-devel
Requires:       pycairo >= 1.2.0
Requires:       dateutil
Requires:       numpy
Requires:       tz

%description
Matplotlib is a pure python plotting library with the goal of making
publication quality plots using a syntax familiar to matlab users. The
library uses Numeric for handling large data sets and supports a variety
of output backends

%prep
%setup -q -n %{name}-%{version}
chmod -x lib/matplotlib/mpl-data/images/*.svg

%build
CFLAGS="${RPM_OPT_FLAGS}" %{__python} setup.py build

%check

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --prefix=${RPM_BUILD_ROOT}%{cat_prefix} --install-data=${RPM_BUILD_ROOT}%{_datadir} --single-version-externally-managed --record=/dev/null
chmod +x %{buildroot}%{python_sitearch}/matplotlib/dates.py

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%doc LICENSE/*
%{python_sitearch}

