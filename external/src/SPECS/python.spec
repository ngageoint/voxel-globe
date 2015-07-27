%include %{_sourcedir}/common.inc
#Tweaking libdir/includedir from common.inc MAY not work well, because python is SO HARD CODED!!!!!

Summary: An interpreted, interactive, object-oriented programming language
Name: Python
Version: 2.7.10
Release: 1%{?dist}
License: Python
Group: Development/Languages
Source: %{name}-%{version}.tar.xz
Source1: common.inc

URL: http://www.python.org/
BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildRequires: readline-devel, openssl-devel, gmp-devel
BuildRequires: ncurses-devel, gdbm-devel, zlib-devel, expat-devel
BuildRequires: libGL-devel tk tix gcc-c++ libX11-devel glibc-devel
BuildRequires: bzip2 tar /usr/bin/find pkgconfig tcl-devel tk-devel
BuildRequires: tix-devel bzip2-devel sqlite-devel
BuildRequires: autoconf
BuildRequires: db4-devel >= 4.7
BuildRequires: libffi-devel
#Requires:       %{name}-libs-static = %{version}-%{release}

%package        libs-static
Summary:	Static Libraries for Python
Group:		Development/Libraries
Requires: 	%{name} = %{version}-%{release}

%package        libs-shared
Summary:	Shared Libraries for Python
Group:		Development/Libraries
Requires: 	%{name} = %{version}-%{release}

%package        devel
Summary:	Development files for Python
Group:		Development/Libraries
Requires: 	%{name} = %{version}-%{release}

%description
Python is an interpreted, interactive, object-oriented programming
language often compared to Tcl, Perl, Scheme or Java. Python includes
modules, classes, exceptions, very high level dynamic data types and
dynamic typing. Python supports interfaces to many system calls and
libraries, as well as to various windowing systems (X11, Motif, Tk,
Mac and MFC).

Programmers can write new built-in modules for Python in C or C++.
Python can be used as an extension language for applications that need
a programmable interface. This package contains most of the standard
Python modules, as well as modules for interfacing to the Tix widget
set for Tk and RPM.

Note that documentation for Python is provided in the python-docs
package.

%description libs-static
The %{name}-libs-static package contains static library for %{name}.

%description libs-shared
The %{name}-libs-shared package contains shared library for %{name}.

%description devel
The %{name}-devel package contains development files for %{name}.

%prep
%setup -q -n %{name}-%{version}

%build
#./configure --prefix=%{_prefix} --enable-shared
./configure --prefix=%{_prefix} --disable-shared --bindir=%{_bindir} --libdir=%{_libdir} --includedir=%{_includedir} --mandir=%{_mandir}
make all %{_smp_mflags}
#I want the static and shared libraries, but I want the end result <strike>static</strike> shared apparently.

%check
LD_LIBRARY_PATH=`pwd`${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
export LD_LIBRARY_PATH
#make test

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
make DESTDIR=$RPM_BUILD_ROOT install
#./configure --prefix=%{_prefix} --disable-shared
./configure --prefix=%{_prefix} --enable-shared --bindir=%{_bindir} --libdir=%{_libdir} --includedir=%{_includedir} --mandir=%{_mandir}
make DESTDIR=$RPM_BUILD_ROOT install
#This'll take longer, but will do what I want >:O

chmod 755 ${RPM_BUILD_ROOT}%{_libdir}/*.a

export LD_LIBRARY_PATH=${RPM_BUILD_ROOT}%{_libdir}${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
${RPM_BUILD_ROOT}%{_bindir}/python -m compileall -x test ${RPM_BUILD_ROOT}%{_libdir}/python2.7/
${RPM_BUILD_ROOT}%{_bindir}/python -O -m compileall -x test ${RPM_BUILD_ROOT}%{_libdir}/python2.7/

#Put special tokens in my config.status file
./configure --prefix=/PrEfIx --libdir=/LiBdIr --includedir=/InClUdEdIr --bindir=/BiNdIr --enable-shared
# --mandir=/MaNdIr Don't care
./python -E -S -m sysconfig --generate-posix-vars
#generate new build/lib*/_sysconfigdata.py with my new tokens

%{__cat} << __EOF__ >> `cat pybuilddir.txt`/_sysconfigdata.py
import os
import sysconfig
paths = sysconfig.get_paths()
from sys import prefix as prefix_path
lib_path = paths['stdlib'];
include_path=paths['include'];
if not lib_path.lower().endswith('lib'):
  lib_path = os.path.split(lib_path)[0];
if not include_path.lower().endswith('include'):
  include_path = os.path.split(include_path)[0];
bin_path=paths['scripts'];

for b in build_time_vars.keys():
  if isinstance(build_time_vars[b], str):
    build_time_vars[b] = build_time_vars[b].replace('/PrEfIx', prefix_path)
    build_time_vars[b] = build_time_vars[b].replace('/LiBdIr', lib_path)
    build_time_vars[b] = build_time_vars[b].replace('/BiNdIr', bin_path)
    build_time_vars[b] = build_time_vars[b].replace('/InClUdEdIr', include_path)
__EOF__

install -m 644 `cat pybuilddir.txt`/_sysconfigdata.py %{buildroot}%{_libdir}/python2.7/

export QA_SKIP_BUILD_ROOT=1
#_sysconfig.py will have some useless references

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%{_bindir}
%{_datadir}
%{_libdir}/python2.7

%files libs-static
%attr (0555,root,root) %{_libdir}/*.a

%files libs-shared
%{_libdir}/*.so*

%files devel
%{_includedir}
%{_libdir}/pkgconfig

%post

%postun

#%changelog

