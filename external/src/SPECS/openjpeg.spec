%include %{_sourcedir}/common.inc

Name:    openjpeg
Version: 2.1.0
Release: 1%{?dist}
Summary: OpenJPEG command line tools

Group:     Applications/Multimedia
License:   BSD
URL:       http://www.openjpeg.org/
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires: cmake
BuildRequires: libtiff-devel

Requires: %{name}-libs = %{version}-%{release}

Source0: %{name}-%{version}.tar.gz
Source1: common.inc


%description
OpenJPEG is an open-source JPEG 2000 codec written in C language. It has been
developed in order to promote the use of JPEG 2000, the new still-image
compression standard from the Joint Photographic Experts Group (JPEG).

%package libs
Summary: JPEG 2000 codec library
Group:   System Environment/Libraries

%description libs
The openjpeg-libs package contains runtime libraries for applications that use
OpenJPEG.

%package  devel
Summary:  Development files for openjpeg
Group:    Development/Libraries
Requires: openjpeg-libs = %{version}-%{release}
Requires: lcms

%description devel
The openjpeg-devel package contains libraries and header files for
developing applications that use OpenJPEG.

%prep
%setup -q -n %{name}-%{version}

# Windows stuff, delete it, it slows down patch making
rm -rf jp3d
# Make sure we use system libraries
rm -rf libs

%build
mkdir build
pushd build

%{__cmake} -DCMAKE_VERBOSE_MAKEFILE=ON \
      -DBUILD_EXAMPLES:BOOL=ON \
      -DCMAKE_INSTALL_LIBDIR:PATH=%{_libdir} \
      -G "Unix Makefiles" \
      -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_INSTALL_PREFIX:PATH=%{_prefix} \
      -DINCLUDE_INSTALL_DIR:PATH=%{_includedir} \
      -DSYSCONF_INSTALL_DIR:PATH=%{_sysconfdir} \
      -DSHARE_INSTALL_PREFIX:PATH=%{_datadir} \
      -DLCMS_INCLUDE_DIR=%{install_dir}%{_includedir} \
      -DLCMS_LIBRARY=%{install_dir}%{_libdir} \
      -DBUILD_SHARED_LIBS:BOOL=ON \
      ..

make %{?_smp_mflags} DESTDIR="%{buildroot}"
popd

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
pushd build
mkdir -p "$RPM_BUILD_ROOT%{_libdir}"
mkdir -p "$RPM_BUILD_ROOT%{_bindir}"
mkdir -p "$RPM_BUILD_ROOT%{_includedir}"
make install DESTDIR="%{buildroot}"
popd

# HACK: until pkg-config support lands, temporarily provide
# openjpeg.h header in legacy location
#ln -s openjpeg/openjpeg.h %{buildroot}%{_includedir}/openjpeg.h

%check
# mostly pointless without test images, but it's a start -- Rex
#make check -C build

echo AEN
echo  %{_bindir}
echo %{_docdir}
 

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%post

%postun

%files
%doc CHANGES LICENSE README
%{_bindir}

%files libs
%{_libdir}/libopenjp2.so.*

%files devel
%{_includedir}
%{_libdir}

%changelog
* Wed Sep 12 2012 Tom Lane <tgl@redhat.com> 1.3-9
- Apply patch for CVE-2012-3535
Resolves: CVE-2012-3535

* Wed Jun 27 2012 Tom Lane <tgl@redhat.com> 1.3-8
- Apply patches for CVE-2009-5030, CVE-2012-3358
Resolves: #831561
- Include -DCMAKE_INSTALL_LIBDIR in cmake call; fixes FTBFS with recent
  versions of cmake

* Wed Jul  7 2010 Tom Lane <tgl@redhat.com> 1.3-7
- Apply two upstream fixes for crasher bugs
Resolves: #609389
- Fix FTBFS: ImplicitDSOLinking (see Fedora bug 564783)

* Mon Nov 30 2009 Dennis Gregorovic <dgregor@redhat.com> - 1.3-6.1
- Rebuilt for RHEL 6

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Fri Jun 19 2009 Rex Dieter <rdieter@fedoraproject.org> - 1.3-5
- libopenjpeg has undefined references (#467661)
- openjpeg.h is installed in a directory different from upstream's default (#484887)
- drop -O3 (#504663)
- add %%check section
- %%files: track libopenjpeg somajor (2)

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Fri Nov 07 2008 Rex Dieter <rdieter@fedoraproject.org> 1.3-3
- FTBFS (#464949)

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 1.3-2
- Autorebuild for GCC 4.3

* Thu Dec 27 2007 Callum Lerwick <seg@haxxed.com> 1.3-1
- New upstream release.

* Tue Dec 11 2007 Callum Lerwick <seg@haxxed.com> 1.2-4.20071211svn484
- New snapshot. Fixes bz420811.

* Wed Nov 14 2007 Callum Lerwick <seg@haxxed.com> 1.2-3.20071114svn480
- Build using cmake.
- New snapshot.

* Thu Aug 09 2007 Callum Lerwick <seg@haxxed.com> 1.2-2.20070808svn
- Put binaries in main package, move libraries to -libs subpackage.

* Sun Jun 10 2007 Callum Lerwick <seg@haxxed.com> 1.2-1
- Build the mj2 tools as well.
- New upstream version, ABI has broken, upstream has bumped soname.

* Fri Mar 30 2007 Callum Lerwick <seg@haxxed.com> 1.1.1-3
- Build and package the command line tools.

* Fri Mar 16 2007 Callum Lerwick <seg@haxxed.com> 1.1.1-2
- Link with libm, fixes building on ppc. i386 and x86_64 are magical.

* Fri Feb 23 2007 Callum Lerwick <seg@haxxed.com> 1.1.1-1
- New upstream version, which has the SL patches merged.

* Sat Feb 17 2007 Callum Lerwick <seg@haxxed.com> 1.1-2
- Move header to a subdirectory.
- Fix makefile patch to preserve timestamps during install.

* Sun Feb 04 2007 Callum Lerwick <seg@haxxed.com> 1.1-1
- Initial packaging.
