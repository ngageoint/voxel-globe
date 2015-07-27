%include %{_sourcedir}/common.inc
#
# Important for %{ix86}:
# This rpm has to be build on a CPU with sse2 support like Pentium 4 !
#

Summary: A GNU arbitrary precision library
Name: gmp
Version: 6.0.0a
Release: 1%{?dist}
URL: http://gmplib.org/
Source0: ftp://ftp.gnu.org/pub/gnu/gmp/%{name}-%{version}.tar.xz
Source1: common.inc
#Source2: gmp.h
#Source3: gmp-mparam.h
# patch s390 gmp-mparam.h to match other archs
#Patch0: gmp-4.0.1-s390.patch
#Patch1: gmp-4.3.1-compat.patch
#Patch2: gmp-4.3.1-macro.patch
# mpn/s390x/gmp-mparam.h: LGPLv2+
# demos/calc/calc.c: GPLv3+
License: LGPLv2+ and  GPLv3+ and LGPLv3+
Group: System Environment/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: autoconf automake libtool

%define version_number %(echo %{version} | grep [0-9.]* -o)

%description
The gmp package contains GNU MP, a library for arbitrary precision
arithmetic, signed integers operations, rational numbers and floating
point numbers. GNU MP is designed for speed, for both small and very
large operands. GNU MP is fast because it uses fullwords as the basic
arithmetic type, it uses fast algorithms, it carefully optimizes
assembly code for many CPUs' most common inner loops, and it generally
emphasizes speed over simplicity/elegance in its operations.

Install the gmp package if you need a fast arbitrary precision
library.

%package devel
Summary: Development tools for the GNU MP arbitrary precision library
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}
Requires(post): /sbin/install-info
Requires(preun): /sbin/install-info

%description devel
The libraries, header files and documentation for using the GNU MP 
arbitrary precision library in applications.

If you want to develop applications which will use the GNU MP library,
you'll need to install the gmp-devel package.  You'll also need to
install the gmp package.

%package static
Summary: Development tools for the GNU MP arbitrary precision library
Group: Development/Libraries
Requires: %{name}-devel = %{version}-%{release}

%description static
The static libraries for using the GNU MP arbitrary precision library 
in applications.

%prep
%setup -q -n %{name}-%{version_number}

%build
autoreconf -if
if as --help | grep -q execstack; then
  # the object files do not require an executable stack
  export CCAS="gcc -c -Wa,--noexecstack"
fi
mkdir base
cd base
ln -s ../configure .
./configure --build=%{_build} --host=%{_host} \
         --program-prefix=%{?_program_prefix} \
         --prefix=%{_prefix} \
         --exec-prefix=%{_exec_prefix} \
         --bindir=%{_bindir} \
         --sbindir=%{_sbindir} \
         --sysconfdir=%{_sysconfdir} \
         --datadir=%{_datadir} \
         --includedir=%{_includedir} \
         --libdir=%{_libdir} \
         --libexecdir=%{_libexecdir} \
         --localstatedir=%{_localstatedir} \
         --sharedstatedir=%{_sharedstatedir} \
         --mandir=%{_mandir} \
         --infodir=%{_infodir} \
         --enable-mpbsd --enable-cxx
#perl -pi -e 's|hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=\"-L\\\$libdir\"|g;' libtool
export LD_LIBRARY_PATH=`pwd`/.libs
#for i in $(find ../ -name Makefile); do \
#    perl -pi -e 'undef $/; s|^PACKAGE_COPYRIGHT =.+?licenses/\.\n\n||sm' "$(readlink -m "$i")"; \
#done
make CFLAGS="$RPM_OPT_FLAGS" %{?_smp_mflags}
cd ..

%ifarch %{ix86}
mkdir build-sse2
cd build-sse2
ln -s ../configure .
CFLAGS="%{optflags} -march=pentium4"
./configure --build=%{_build} --host=%{_host} \
         --program-prefix=%{?_program_prefix} \
         --prefix=%{_prefix} \
         --exec-prefix=%{_exec_prefix} \
         --bindir=%{_bindir} \
         --sbindir=%{_sbindir} \
         --sysconfdir=%{_sysconfdir} \
         --datadir=%{_datadir} \
         --includedir=%{_includedir} \
         --libdir=%{_libdir} \
         --libexecdir=%{_libexecdir} \
         --localstatedir=%{_localstatedir} \
         --sharedstatedir=%{_sharedstatedir} \
         --mandir=%{_mandir} \
         --infodir=%{_infodir} \
         --enable-mpbsd --enable-cxx
#perl -pi -e 's|hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=\"-L\\\$libdir\"|g;' libtool
export LD_LIBRARY_PATH=`pwd`/.libs
#for i in $(find ../ -name Makefile); do \
#    perl -pi -e 'undef $/; s|^PACKAGE_COPYRIGHT =.+?licenses/\.\n\n||sm' "$(readlink -m "$i")"; \
#done
make %{?_smp_mflags}
unset CFLAGS
cd ..
%endif

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
cd base
export LD_LIBRARY_PATH=`pwd`/.libs
make install DESTDIR=$RPM_BUILD_ROOT
install -m 644 gmp-mparam.h ${RPM_BUILD_ROOT}%{_includedir}
rm -f $RPM_BUILD_ROOT%{_libdir}/lib{gmp,mp,gmpxx}.la
rm -f $RPM_BUILD_ROOT%{_infodir}/dir
/sbin/ldconfig -n $RPM_BUILD_ROOT%{_libdir}
ln -sf libgmpxx.so.4 $RPM_BUILD_ROOT%{_libdir}/libgmpxx.so
cd ..
%ifarch %{ix86}
cd build-sse2
export LD_LIBRARY_PATH=`pwd`/.libs
mkdir $RPM_BUILD_ROOT%{_libdir}/sse2
install -m 755 .libs/libgmp.so.3.* $RPM_BUILD_ROOT%{_libdir}/sse2
cp -a .libs/libgmp.so.3 $RPM_BUILD_ROOT%{_libdir}/sse2
chmod 755 $RPM_BUILD_ROOT%{_libdir}/sse2/libgmp.so.3
install -m 755 .libs/libgmpxx.so.4.* $RPM_BUILD_ROOT%{_libdir}/sse2
cp -a .libs/libgmpxx.so.4 $RPM_BUILD_ROOT%{_libdir}/sse2
chmod 755 $RPM_BUILD_ROOT%{_libdir}/sse2/libgmpxx.so.4
install -m 755 .libs/libmp.so.3.* $RPM_BUILD_ROOT%{_libdir}/sse2
cp -a .libs/libmp.so.3 $RPM_BUILD_ROOT%{_libdir}/sse2
chmod 755 $RPM_BUILD_ROOT%{_libdir}/sse2/libmp.so.3
cd ..
%endif

# Rename gmp.h to gmp-<arch>.h and gmp-mparam.h to gmp-mparam-<arch>.h to 
# avoid file conflicts on multilib systems and install wrapper include files
# gmp.h and gmp-mparam-<arch>.h
basearch=%{_arch}
# always use i386 for iX86
%ifarch %{ix86}
basearch=i386
%endif
# always use arm for arm*
%ifarch %{arm}
basearch=arm
%endif
# superH architecture support
%ifarch sh3 sh4
basearch=sh
%endif
# Rename files and install wrappers

#mv %{buildroot}/%{_includedir}/gmp.h %{buildroot}/%{_includedir}/gmp-${basearch}.h
#install -m644 %{SOURCE2} %{buildroot}/%{_includedir}/gmp.h
#mv %{buildroot}/%{_includedir}/gmp-mparam.h %{buildroot}/%{_includedir}/gmp-mparam-${basearch}.h
#install -m644 %{SOURCE3} %{buildroot}/%{_includedir}/gmp-mparam.h


%check
%ifnarch ppc
cd base
export LD_LIBRARY_PATH=`pwd`/.libs
make %{?_smp_mflags} check
cd ..
%endif
%ifarch %{ix86}
cd build-sse2
export LD_LIBRARY_PATH=`pwd`/.libs
make %{?_smp_mflags} check
cd ..
%endif

%post

%postun

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc COPYING* NEWS README
%{_libdir}/libgmp.so.*
#%{_libdir}/libmp.so.*
%{_libdir}/libgmpxx.so.*
%ifarch %{ix86}
%{_libdir}/sse2/*
%endif

%files devel
%defattr(-,root,root,-)
#%{_libdir}/libmp.so
%{_libdir}/libgmp.so
%{_libdir}/libgmpxx.so
%{_includedir}/*.h
%{_infodir}/gmp.info*

%files static
%defattr(-,root,root,-)
#%{_libdir}/libmp.a
%{_libdir}/libgmp.a
%{_libdir}/libgmpxx.a


%changelog
* Fri Mar 02 2012 Peter Schiffer <pschiffe@redhat.com> - 4.3.1-7.el6_2.2
- Related: #798771
  fixed FTBFS on some hosts

* Wed Feb 29 2012 Peter Schiffer <pschiffe@redhat.com> - 4.3.1-7.el6_2.1
- Resolves: #798771
  readded missing '__gmp_doprnt_mpf' symbol

* Wed Feb 24 2010 Ivama Hutarova Varekova <varekova@redhat.com> - 4.3.1-7
- Resolves: #543948
  fix license tag

* Thu Dec 03 2009 Dennis Gregorovic <dgregor@redhat.com> - 4.3.1-6.1
- Rebuilt for RHEL 6

* Fri Nov 27 2009 Ivana Hutarova Varekova <varekova@redhat.com> - 4.3.1-6
- remove unnecessary dependences
  remove duplicated documentation

* Mon Aug 10 2009 Ivana Varekova <varekova@redhat.com> 4.3.1-5
- fix installation with --excludedocs option (#515947)

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.3.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Jun 17 2009 Ivana Varekova <varekova@redhat.com> 4.3.1-3
- rebuild

* Mon Jun 15 2009 Ivana Varekova <varekova@redhat.com> 4.3.1-2
- Resolves: #505592
  add RPM_OPT_FLAGS

* Thu May 28 2009 Ivana Varekova <varekova@redhat.com> 4.3.1-1
- update to 4.3.1
- remove configure macro (built problem)

* Thu Apr 09 2009 Dennis Gilmore <dennis@ausil.us> - 4.2.4-6
- no check that --host and --target are the same when building i586  or sparcv9 they are not

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.2.4-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Tue Dec 23 2008 Ivana Varekova <varekova@redhat.com> 4.2.4-4
- fix spec file

* Mon Dec  8 2008 Ivana Varekova <varekova@redhat.com> 4.2.4-3
- remove useless option (#475073)

* Wed Dec  3 2008 Stepan Kasal <skasal@redhat.com> 4.2.4-2
- Run full autoreconf, add automake to BuildRequires.

* Mon Nov 10 2008 Ivana Varekova <varekova@redhat.com> 4.2.4-1
- update to 4.2.4

* Fri Nov  7 2008 Ivana Varekova <varekova@redhat.com> 4.2.2-9
- remove useless patch (#470200)

* Thu Apr 24 2008 Tom "spot" Callaway <tcallawa@redhat.com> 4.2.2-8
- add sparc/sparc64 support

* Wed Mar 19 2008 Ivana Varekova <varekova@redhat.com> 4.2.2-7
- add superH support (#437688)

* Wed Feb 13 2008 Ivana varekova <varekova@redhat.com> 4.2.2-6
- fix gcc-4.3 problem - add <cstdio> (#432336)

* Fri Feb  8 2008 Ivana Varekova <varekova@redhat.com> 4.2.2-5
- split the devel subpackage to devel and static parts

* Thu Feb  7 2008 Ivana Varekova <varekova@redhat.com> 4.2.2-4
- change license tag

* Mon Sep 24 2007 Ivana Varekova <varekova@redhat.com> 4.2.2-3
- fix libgmpxx.so link

* Thu Sep 20 2007 Ivana Varekova <varekova@redhat.com> 4.2.2-2
- fix check tag

* Wed Sep 19 2007 Ivana Varekova <varekova@redhat.com> 4.2.2-1
- update to 4.2.2

* Mon Aug 20 2007 Ivana Varekova <varekova@redhat.com> 4.2.1-3
- spec file cleanup (#253439)

* Tue Aug  7 2007 Ivana Varekova <varekova@redhat.com> 4.2.1-2
- add arm support (#245456)
  thanks to Lennert Buytenhek

* Mon Aug  6 2007 Ivana Varekova <varekova@redhat.com> 4.2.1-1
- update to 4.2.1
- do some spec cleanups
- fix 238794 - gmp-devel depends on {version} but not on 
  {version}-{release}
- remove mpfr (moved to separate package)

* Thu Jul 05 2007 Florian La Roche <laroche@redhat.com> 4.1.4-13
- don't fail scripts to e.g. allow excludedocs installs

* Tue Apr 24 2007 Karsten Hopp <karsten@redhat.com> 4.1.4-12.3
- fix library permissions

* Wed Mar 14 2007 Karsten Hopp <karsten@redhat.com> 4.1.4-12.2
- fix typo

* Wed Mar 14 2007 Thomas Woerner <twoerner@redhat.com> 4.1.4-12.1
- added alpha support for gmp.h and gmp-mparam.h wrappers

* Fri Feb 23 2007 Karsten Hopp <karsten@redhat.com> 4.1.4-12
- remove trailing dot from summary
- fix buildroot
- fix post/postun/... requirements
- use make install DESTDIR=...
- replace tabs with spaces
- convert changelog to utf-8

* Wed Jan 17 2007 Jakub Jelinek <jakub@redhat.com> 4.1.4-11
- make sure libmpfr.a doesn't contain SSE2 instructions on i?86 (#222371)
- rebase to mpfr 2.2.1 from 2.2.0 + cumulative fixes

* Thu Nov  2 2006 Thomas Woerner <twoerner@redhat.com> 4.1.4-10
- fixed arch order in gmp.h and gmp-mparam.h wrapper for all architectures

* Thu Nov  2 2006 Joe Orton <jorton@redhat.com> 4.1.4-10
- include ppc64 header on ppc64 not ppc header

* Fri Oct 27 2006 Thomas Woerner <twoerner@redhat.com> - 4.1.4-9
- fixed multilib devel conflicts for gmp (#212286)

* Thu Oct 26 2006 Jakub Jelinek <jakub@redhat.com> - 4.1.4-8
- upgrade mpfr to 2.2.0 (#211971)
- apply mpfr 2.2.0 cumulative patch

* Fri Jul 14 2006 Thomas Woerner <twoerner@redhat.com> - 4.1.4-7
- release bump

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 4.1.4-6.2.1
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 4.1.4-6.2
- rebuilt for new gcc4.1 snapshot and glibc changes

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Mon Apr 18 2005 Thomas Woerner <twoerner@redhat.com> 4.1.4-6
- fixed __setfpucw call in mpfr-test.h

* Wed Mar 02 2005 Karsten Hopp <karsten@redhat.de> 4.1.4-5
- build with gcc-4

* Wed Feb 09 2005 Karsten Hopp <karsten@redhat.de> 4.1.4-4
- rebuilt

* Sun Sep 26 2004 Florian La Roche <Florian.LaRoche@redhat.de>
- 4.1.4
- disable ppc64 patch, now fixed upstream

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Mon May 24 2004 Thomas Woerner <twoerner@redhat.com> 4.1.3-1
- new version 4.1.3

* Wed Mar 31 2004 Thomas Woerner <twoerner@redhat.com> 4.1.2-14
- dropped RPATH (#118506)

* Sat Mar 06 2004 Florian La Roche <Florian.LaRoche@redhat.de>
- also build SSE2 DSOs, patch from Ulrich Drepper

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Thu Jan 29 2004 Thomas Woerner <twoerner@redhat.com> 4.1.2-11
- BuildRequires for automake16

* Mon Dec 01 2003 Florian La Roche <Florian.LaRoche@redhat.de>
- fix symlink to libgmpxx.so.3  #111135
- add patch to factorize.c from gmp homepage

* Thu Oct 23 2003 Joe Orton <jorton@redhat.com> 4.1.2-9
- build with -Wa,--noexecstack

* Thu Oct 23 2003 Joe Orton <jorton@redhat.com> 4.1.2-8
- build assembly code with -Wa,--execstack
- use parallel make
- run tests, and fix C++ therein

* Thu Oct 02 2003 Florian La Roche <Florian.LaRoche@redhat.de>
- enable mpfr  #104395
- enable cxx  #80195
- add COPYING.LIB
- add fixes from gmp web-site
- remove some cruft patches for older libtool releases

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Jun 03 2003 Florian La Roche <Florian.LaRoche@redhat.de>
- make configure.in work with newer autoconf

* Sun Jun 01 2003 Florian La Roche <Florian.LaRoche@redhat.de>
- do not set extra_functions for s390x  #92001

* Thu Feb 13 2003 Elliot Lee <sopwith@redhat.com> 4.1.2-3
- Add ppc64 patch, accompanied by running auto*

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Wed Jan 01 2003 Florian La Roche <Florian.LaRoche@redhat.de>
- update to 4.1.2

* Tue Dec 03 2002 Florian La Roche <Florian.LaRoche@redhat.de>
- update to 4.1.1
- remove un-necessary patches
- adjust s390/x86_64 patch

* Sun Oct 06 2002 Florian La Roche <Florian.LaRoche@redhat.de>
- add s390x patch
- disable current x86-64 support in longlong.h

* Mon Jul  8 2002 Trond Eivind Glomsrød <teg@redhat.com> 4.1-4
- Add 4 patches, among them one for #67918
- Update URL
- s/Copyright/License/

* Mon Jul  8 2002 Trond Eivind Glomsrød <teg@redhat.com> 4.1-3
- Redefine the configure macro, the included configure 
  script isn't happy about the rpm default one (#68190). Also, make
  sure the included libtool isn't replaced,

* Fri Jun 21 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Sat May 25 2002 Florian La Roche <Florian.LaRoche@redhat.de>
- update to version 4.1
- patch s390 gmp-mparam.h to match other archs.

* Thu May 23 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Mon Mar 11 2002 Trond Eivind Glomsrød <teg@redhat.com> 4.0.1-3
- Use standard %%configure macro and edit %%{_tmppath}

* Tue Feb 26 2002 Trond Eivind Glomsrød <teg@redhat.com> 4.0.1-2
- Rebuild

* Tue Jan 22 2002 Florian La Roche <Florian.LaRoche@redhat.de>
- update to 4.0.1
- bzip2 src

* Wed Jan 09 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Sun Jun 24 2001 Elliot Lee <sopwith@redhat.com>
- Bump release + rebuild.

* Mon Feb 05 2001 Philipp Knirsch <pknirsch@redhat.de>
- Fixed bugzilla bug #25515 where GMP wouldn't work on IA64 as IA64 is not
correctly identified as a 64 bit platform.

* Mon Dec 18 2000 Preston Brown <pbrown@redhat.com>
- include bsd mp library

* Tue Oct 17 2000 Florian La Roche <Florian.LaRoche@redhat.de>
- update to 3.1.1

* Sun Sep  3 2000 Florian La Roche <Florian.LaRoche@redhat.com>
- update to 3.1

* Sat Aug 19 2000 Preston Brown <pbrown@redhat.com>
- devel subpackage depends on main package so that .so symlink is OK.

* Thu Jul 13 2000 Prospector <bugzilla@redhat.com>
- automatic rebuild

* Sat Jun  3 2000 Nalin Dahyabhai <nalin@redhat.com>
- switch to the configure and makeinstall macros
- FHS-compliance fixing
- move docs to non-devel package

* Fri Apr 28 2000 Bill Nottingham <notting@redhat.com>
- libtoolize for ia64

* Fri Apr 28 2000 Florian La Roche <Florian.LaRoche@redhat.com>
- update to 3.0.1

* Thu Apr 27 2000 Jakub Jelinek <jakub@redhat.com>
- sparc64 fixes for 3.0

* Wed Apr 26 2000 Florian La Roche <Florian.LaRoche@redhat.com>
- update to 3.0

* Mon Feb 14 2000 Matt Wilson <msw@redhat.com>
- #include <string.h> in files that use string functions

* Wed Feb 02 2000 Cristian Gafton <gafton@redhat.com>
- fix description and summary

* Mon Dec 06 1999 Michael K. Johnson <johnsonm@redhat.com>
- s/GPL/LGPL/
- build as non-root (#7604)

* Mon Sep 06 1999 Jakub Jelinek <jj@ultra.linux.cz>
- merge in some debian gmp fixes
- Ulrich Drepper's __gmp_scale2 fix
- my mpf_set_q fix
- sparc64 fixes

* Wed Apr 28 1999 Cristian Gafton <gafton@redhat.com>
- add sparc patch for PIC handling

* Sun Mar 21 1999 Cristian Gafton <gafton@redhat.com> 
- auto rebuild in the new build environment (release 8)

* Thu Feb 11 1999 Michael Johnson <johnsonm@redhat.com>
- include the private header file gmp-mparam.h because several
  apps seem to assume that they are building against the gmp
  source tree and require it.  Sigh.

* Tue Jan 12 1999 Michael K. Johnson <johnsonm@redhat.com>
- libtoolize to work on arm

* Thu Sep 10 1998 Cristian Gafton <gafton@redhat.com>
- yet another touch of the spec file

* Wed Sep  2 1998 Michael Fulbright <msf@redhat.com>
- looked over before inclusion in RH 5.2

* Sat May 24 1998 Dick Porter <dick@cymru.net>
- Patch Makefile.in, not Makefile
- Don't specify i586, let configure decide the arch

* Sat Jan 24 1998 Marc Ewing <marc@redhat.com>
- started with package from Toshio Kuratomi <toshiok@cats.ucsc.edu>
- cleaned up file list
- fixed up install-info support

