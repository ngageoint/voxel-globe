%include %{_sourcedir}/common.inc

Name:           lcms
Version:        1.19
Release:        1%{?dist}
Summary:        Color Management System

Group:          Applications/Productivity
License:        MIT
URL:            http://www.littlecms.com/
Source0:        http://www.littlecms.com/%{name}-%{version}.tar.gz
Source1:        common.inc
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  libjpeg-devel
BuildRequires:  libtiff-devel
BuildRequires:  pkgconfig
BuildRequires:  python-devel
BuildRequires:  swig >= 1.3.12
BuildRequires:  zlib-devel

Provides:       littlecms = %{version}-%{release}
Requires:       %{name}-libs = %{version}-%{release}

%description
LittleCMS intends to be a small-footprint, speed optimized color management
engine in open source form.

%package        libs
Summary:        Library for %{name}
Group:          System Environment/Libraries
# Introduced in F-9 to solve multilib transition
Obsoletes:      lcms < 1.17-3

%description    libs
The %{name}-libs package contains library for %{name}.

%package     -n python-%{name}
Summary:        Python interface to LittleCMS
Group:          Development/Libraries
Requires:       python
Provides:       python-littlecms = %{version}-%{release}

%description -n python-%{name}
Python interface to LittleCMS.


%package        devel
Summary:        Development files for LittleCMS
Group:          Development/Libraries
Requires:       %{name}-libs = %{version}-%{release}
Requires:       pkgconfig
Provides:       littlecms-devel = %{version}-%{release}

%description    devel
Development files for LittleCMS.

%prep
%setup -q

find . -name \*.[ch] | xargs chmod -x
chmod 0644 AUTHORS COPYING ChangeLog NEWS README.1ST doc/TUTORIAL.TXT doc/LCMSAPI.TXT

# Convert not UTF-8 files
pushd doc
mkdir -p __temp
for f in LCMSAPI.TXT TUTORIAL.TXT ;do
cp -p $f __temp/$f
iconv -f ISO-8859-1 -t UTF-8 __temp/$f > $f
touch -r __temp/$f $f
done
rm -rf __temp
popd

%build
%configure --with-python --disable-static

# remove rpath from libtool
#sed -i.rpath 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
#sed -i.rpath 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool

(cd python; ./swig_lcms)

make %{?_smp_mflags} LCMS_PYEXECDIR=/lib/python2.7/site-packages

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
make install DESTDIR=${RPM_BUILD_ROOT} INSTALL="install -p" LCMS_PYEXECDIR=%{python_sitearch}
mkdir -p ${RPM_BUILD_ROOT}%{_libdir}/la
find ${RPM_BUILD_ROOT} -type f -name "*.la" -exec mv {} ${RPM_BUILD_ROOT}%{_libdir}/la/ ';'

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%post

%postun

%files
%doc README.1ST doc/TUTORIAL.TXT
%{_bindir}/*
%{_mandir}/man1/*

%files libs
%doc AUTHORS COPYING NEWS
%{_libdir}/*.so.*

%files devel
%doc doc/LCMSAPI.TXT
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/pkgconfig/%{name}.pc
%{_libdir}/la/*.la

%files -n python-%{name}
%{python_sitearch}/lcms.py*
%{python_sitearch}/_lcms.so
