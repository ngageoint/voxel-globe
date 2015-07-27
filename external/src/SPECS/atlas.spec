%include %{_sourcedir}/common.inc
%define debug_package %{nil}
#Prevents ERROR: No build ID note found in

Name:           atlas
%define source_dir_name %(x=%{name}; echo ${x^^})
Version:        3.10.2
Release:        1%{?dist}
Summary:        Automatically Tuned Linear Algebra Software

Group:          System Environment/Libraries
License:        BSD
URL:            http://math-atlas.sourceforge.net/
Source0:        http://downloads.sourceforge.net/math-atlas/%{name}%{version}.tar.bz2
Source1:        common.inc
Source2:        lapack-3.5.0.tgz

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:  gcc-gfortran lapack-devel lapack-static

%description
The ATLAS (Automatically Tuned Linear Algebra Software) project is an
ongoing research effort focusing on applying empirical techniques in
order to provide portable performance. At present, it provides C and
Fortran77 interfaces to a portably efficient BLAS implementation, as
well as a few routines from LAPACK.

The performance improvements in ATLAS are obtained largely via
compile-time optimizations and tend to be specific to a given hardware
configuration. In order to package ATLAS for Red Hat Enterprise Linux
some compromises are necessary so that good performance can be obtained
on a variety of hardware. This set of ATLAS binary packages is therefore
not necessarily optimal for any specific hardware configuration.
However, the source package can be used to compile customized ATLAS
packages; see the documentation for information.

%package devel
Summary:        Development libraries for ATLAS
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}
Obsoletes:	%name-header <= %version-%release

%description devel
This package contains the static libraries and headers for development
with ATLAS (Automatically Tuned Linear Algebra Software).


%prep
%setup -q -n %{source_dir_name}

#Fix some STUPID error in ATLAS, that I have NO IDEA why it hasn't been fixed!
sed -i 's@soname $(LIBINSTdir)/@soname @g' makes/Make.lib

if [ "${VIP_ATLAS_SKIP_THROTTLE_CHECK}" == "1" ]; then
  for i in $(seq 1 10); do
    echo '#######################################################################################'
  done
  echo WHAT ARE YOU DOING? INSTALLING ATLAS without CPU in performance mode is BAD! The Library
  echo Can take up to a DAY to compile and will not be optimized at ALL for your computer, it will
  echo be SLOW SLOW SLOW!!! Only do this for proof of concept, GET ROOT and run:
  echo Just do it! No more execuses!!!!
  echo .
  echo ..
  echo ...
  echo "Alright, I'll disable throttle checking, but I warned you!!!"
  for i in $(seq 1 10); do
    echo '#######################################################################################'
  done
  sleep 10

  #Disable throttle checking... may your code rest in silicon..., you know. 
  sed -i 's|\*ThrChk = 1|*ThrChk = 0|' CONFIG/src/config.c
fi

%build
libname=atlas
mkdir -p %{_arch}
pushd %{_arch}

cpu=0
while [ $cpu -lt $(nproc) ]; do
  if [ "$(cat /sys/devices/system/cpu/cpu${cpu}/cpufreq/scaling_governor)" != "performance" ]; then 
    echo CPUs are NOT in performance mode. This prevents ATLAS optimization
    echo Enter the following as root
    echo sudo bash -c \''cpu=0; while [ $cpu -lt $(nproc) ]; do echo performance > /sys/devices/system/cpu/cpu${cpu}/cpufreq/scaling_governor; let cpu=cpu+1; done'\'
  fi
  let cpu=cpu+1
done 

../configure -b %{__isa_bits} -D c -DWALL \
	-Fa alg '-g -Wa,--noexecstack -fPIC' \
	--prefix=%{buildroot}%{_prefix}	\
	--incdir=%{buildroot}%{_includedir}	\
	--libdir=%{buildroot}%{_libdir} \
%if 0%{?rhel} && 0%{?rhel}<7
    -V 480 -A 27 \
%endif
	--with-netlib-lapack-tarfile=%{SOURCE2}
#The V 480 A27 basically forces an Corei2 without AVX2... Rhel before 7 is gcc <4.7 which is required for ATLAS cause it uses avx2
#This is a crap fix because it assumes you have at least a Corei2... It could be made better, but I have to disable AVX2 and V480
#disables it, while V488 enables it. A28 is Corei3... untested in rhel7, but should work?

make build
cd lib
make shared
make ptshared
popd

%install
rm -rf %{buildroot}

pushd %{_arch}
make DESTDIR=%{buildroot} install
mv %{buildroot}%{_includedir}/atlas %{buildroot}%{_includedir}/atlas-%{_arch}
popd


%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc doc/*
%dir %{_libdir}
%{_libdir}/*.so

%files devel
%defattr(-,root,root,-)
%doc doc
%{_libdir}/*.a
%{_includedir}/atlas-%{_arch}/
%{_includedir}/*.h

%changelog
* Thu Feb 09 2012 Peter Schiffer <pschiffe@redhat.com> 3.8.4-2
- Resolves: #723350
  Removed illegal 3DNow instruction set from the base package.

* Fri Jul 08 2011 Petr Lautrbach <plautrba@redhat.com> 3.8.4-1
- Update to 3.8.4
- Optimized build and subpackages -z10 and -z196 for Linux on System z (#694459)

* Thu Jun 10 2010 Petr Lautrbach <plautrba@redhat.com> 3.8.3-12.4
- Documentation fix
- Resolves: rhbz#596658

* Thu Jan 28 2010 Petr Lautrbach <plautrba@redhat.com> 3.8.3-12.3
- Ignore CPU throttling probe
- Resolves: rhbz#558894

* Mon Dec 14 2009 Petr Lautrbach <plautrba@redhat.com> - 3.8.3-12.2
- Use -m31 for the s390 gcc
- Resolves: rhbz#547277

* Mon Nov 30 2009 Dennis Gregorovic <dgregor@redhat.com> - 3.8.3-12.1
- Rebuilt for RHEL 6

* Sat Oct 24 2009 Deji Akingunola <dakingun@gmail.com> - 3.8.3-12
- Use alternatives to workaround multilib conflicts (BZ#508565). 

* Tue Sep 29 2009 Deji Akingunola <dakingun@gmail.com> - 3.8.3-11
- Obsolete the -header subpackage properly. 

* Sat Sep 26 2009 Deji Akingunola <dakingun@gmail.com> - 3.8.3-10
- Use the new arch. default for Pentium PRO (Fedora bug #510498)
- (Re-)Introduce 3dNow subpackage

* Sun Sep  6 2009 Alex Lancaster <alexlan[AT]fedoraproject org> - 3.8.3-9
- Rebuild against fixed lapack (see #520518)

* Wed Aug 13 2009 Deji Akingunola <dakingun@gmail.com> - 3.8.3-8
- Revert the last change, it doesn't solve the problem. 

* Tue Aug 04 2009 Deji Akingunola <dakingun@gmail.com> - 3.8.3-7
- Create a -header subpackage to avoid multilib conflicts (BZ#508565). 

* Tue Aug 04 2009 Deji Akingunola <dakingun@gmail.com> - 3.8.3-6
- Add '-g' to build flag to allow proper genration of debuginfo subpackages (Fedora bug #509813)
- Build for F12

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.8.3-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Sat May 02 2009 Deji Akingunola <dakingun@gmail.com> - 3.8.3-4
- Use the right -msse* option for the -sse* subpackages (Fedora bug #498715)

* Tue Apr 21 2009 Karsten Hopp <karsten@redhat.com> 3.8.3-3.1
- add s390x to 64 bit archs

* Fri Feb 27 2009 Deji Akingunola <dakingun@gmail.com> - 3.8.3-3
- Rebuild

* Mon Feb 23 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.8.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sun Feb 22 2009 Deji Akingunola <dakingun@gmail.com> - 3.8.3-1
- Update to version 3.8.3

* Sun Dec 21 2008 Deji Akingunola <dakingun@gmail.com> - 3.8.2-5
- Link in appropriate libs when creating shared libs, reported by Orcan 'oget' Ogetbil (BZ#475411)

* Tue Dec 16 2008 Deji Akingunola <dakingun@gmail.com> - 3.8.2-4
- Don't symlink the atlas libdir on i386, cause upgrade issue (BZ#476787)
- Fix options passed to gcc when making shared libs

* Tue Dec 16 2008 Deji Akingunola <dakingun@gmail.com> - 3.8.2-3
- Use 'gcc -shared' to build shared libs instead of stock 'ld'

* Sat Dec 13 2008 Deji Akingunola <dakingun@gmail.com> - 3.8.2-2
- Properly obsolete/provide older subpackages that are no longer packaged.

* Mon Sep 01 2008 Deji Akingunola <dakingun@gmail.com> - 3.8.2-1
- Upgrade to ver 3.8.2 with refined build procedures.

* Thu Feb 28 2008 Quentin Spencer <qspencer@users.sourceforge.net> 3.6.0-15
- Disable altivec package--it is causing illegal instructions during build.

* Thu Feb 28 2008 Quentin Spencer <qspencer@users.sourceforge.net> 3.6.0-14
- Enable compilation on alpha (bug 426086).
- Patch for compilation on ia64 (bug 432744).

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 3.6.0-13
- Autorebuild for GCC 4.3

* Mon Jun  4 2007 Orion Poplawski <orion@cora.nwra.com> 3.6.0-12
- Rebuild for ppc64

* Fri Sep  8 2006 Quentin Spencer <qspencer@users.sourceforge.net> 3.6.0-11
- Rebuild for FC6.
- Remove outdated comments from spec file.

* Mon Feb 13 2006 Quentin Spencer <qspencer@users.sourceforge.net> 3.6.0-10
- Rebuild for Fedora Extras 5.
- Add --noexecstack to compilation of assembly kernels. These were
  previously marked executable, which caused problems with selinux.

* Mon Dec 19 2005 Quentin Spencer <qspencer@users.sourceforge.net> 3.6.0-9
- Rebuild for gcc 4.1.

* Mon Oct 10 2005 Quentin Spencer <qspencer@users.sourceforge.net> 3.6.0-8
- Make all devel subpackages depend on their non-devel counterparts.
- Add /etc/ld.so.conf.d files for -sse and -3dnow, because they don't
  seem to get picked up automatically.

* Wed Oct 05 2005 Quentin Spencer <qspencer@users.sourceforge.net> 3.6.0-7
- Forgot to add the new patch to sources.

* Tue Oct 04 2005 Quentin Spencer <qspencer@users.sourceforge.net> 3.6.0-6
- Use new Debian patch, and enable shared libs (they previously failed
  to build on gcc 4).
- Minor updates to description and README.Fedora file.
- Fix buildroot name to match FE preferred form.
- Fixes for custom optimized builds.
- Add dist tag.

* Wed Sep 28 2005 Quentin Spencer <qspencer@users.sourceforge.net> 3.6.0-5
- fix files lists.

* Mon Sep 26 2005 Quentin Spencer <qspencer@users.sourceforge.net> 3.6.0-4
- generate library symlinks earlier for the benefit of later linking steps.

* Wed Sep 14 2005 Quentin Spencer <qspencer@users.sourceforge.net> 3.6.0-3
- Change lapack dependency to lapack-devel, and use lapack_pic.a for
  building liblapack.so.

* Wed Sep 14 2005 Quentin Spencer <qspencer@users.sourceforge.net> 3.6.0-2
- Add "bit" macro to correctly build on x86_64.

* Tue Aug 16 2005 Quentin Spencer <qspencer@users.sourceforge.net> 3.6.0-1
- Initial version.
