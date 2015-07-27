%include %{_sourcedir}/common.inc

Name:           lcms2
Version:        2.7
Release:        1%{?dist}
Summary:        Color Management Engine

Group:          Applications/Productivity
License:        MIT
URL:            http://www.littlecms.com/
Source0:        http://www.littlecms.com/%{name}-%{version}.tar.gz
Source1:        common.inc
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  libjpeg-devel
BuildRequires:  libtiff-devel
BuildRequires:  zlib-devel

Provides:       lcms2 = %{version}-%{release}
Requires:       %{name}-libs = %{version}-%{release}

%description
LittleCMS intends to be a small-footprint, speed optimized color management
engine in open source form. LCMS2 is the current version of LCMS, and can be
parallel installed with the original (deprecated) lcms.

%package        libs
Summary:        Library for %{name}
Group:          System Environment/Libraries
# Introduced in F-9 to solve multilib transition
Obsoletes:      lcms2 < %{version}

%description    libs
The %{name}-libs package contains library for %{name}.

%package        devel
Summary:        Development files for LittleCMS
Group:          Development/Libraries
Requires:       %{name}-libs = %{version}-%{release}
Requires:       pkgconfig
Provides:       lcms2-devel = %{version}-%{release}

%description    devel
Development files for LittleCMS.

%prep
%setup -q

%build
%configure --program-suffix=2
make %{?_smp_mflags} LCMS_PYEXECDIR=/lib/python2.7/site-packages

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
make install DESTDIR=${RPM_BUILD_ROOT} INSTALL="install -p" LCMS_PYEXECDIR=%{python_sitearch}

install -D -m 644 include/lcms2.h $RPM_BUILD_ROOT%{_includedir}/lcms2.h
install -D -m 644 include/lcms2_plugin.h $RPM_BUILD_ROOT%{_includedir}/lcms2_plugin.h

install -D -m 644 doc/LittleCMS2.?\ tutorial.pdf $RPM_BUILD_ROOT%{_docdir}/lcms2-devel-%{version}/tutorial.pdf
install -D -m 644 doc/LittleCMS2.?\ API.pdf $RPM_BUILD_ROOT%{_docdir}/lcms2-devel-%{version}/api.pdf
install -D -m 644 doc/LittleCMS2.?\ Plugin\ API.pdf $RPM_BUILD_ROOT%{_docdir}/lcms2-devel-%{version}/plugin-api.pdf

mkdir -p $RPM_BUILD_ROOT%{_libdir}/la
mv $RPM_BUILD_ROOT%{_libdir}/*.la $RPM_BUILD_ROOT%{_libdir}/la

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%post

%postun

%files
%doc README.1ST
%{_bindir}/*
%{_mandir}/man1/*

%files libs
%doc AUTHORS COPYING
%{_libdir}/*.so.*

%files devel
%{_docdir}
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/*.a
%{_libdir}/la/*.la
%{_libdir}/pkgconfig/%{name}.pc

