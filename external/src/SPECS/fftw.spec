%include %{_sourcedir}/common.inc

Name:           fftw
Version:        3.3.4
Release:        1%{?dist}
Summary:        Fast Fourier Transform library
Group:          System Environment/Libraries
License:        GPLv2+
URL:            http://www.fftw.org/
Source0:        ftp://ftp.fftw.org/pub/fftw/%{name}-%{version}.tar.gz
Source1:        common.inc
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  gcc-gfortran

Provides:       fftw3 = %{version}-%{release}
Obsoletes:      fftw3 < 3.1

%description
FFTW is a C subroutine library for computing the Discrete Fourier
Transform (DFT) in one or more dimensions, of both real and complex
data, and of arbitrary input size.


%package        devel
Summary:        Headers, libraries and docs for the FFTW library
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release} pkgconfig

Provides:       fftw3-devel = %{version}-%{release}
Obsoletes:      fftw3-devel < 3.1


%description    devel
FFTW is a C subroutine library for computing the Discrete Fourier
Transform (DFT) in one or more dimensions, of both real and complex
data, and of arbitrary input size.

This package contains header files and development libraries needed to
develop programs using the FFTW fast Fourier transform library.


%package        static
Summary:        Static version of the FFTW library
Group:          Development/Libraries
Requires:       %{name}-devel = %{version}-%{release}
Provides:       fftw3-static = %{version}-%{release}

%description    static
The fftw-static package contains the statically linkable version of
the FFTW fast Fourier transform library.


%prep
%setup -q -c %{name}-%{version}
mv %{name}-%{version} single
cp -a single double
cp -a single long


%build
CONFIG_FLAGS="--enable-shared --disable-dependency-tracking --enable-threads"
pushd double
	%configure $CONFIG_FLAGS
	make %{?_smp_mflags}
popd
pushd single
	%configure $CONFIG_FLAGS --enable-single
	make %{?_smp_mflags}
popd
pushd long
	%configure $CONFIG_FLAGS --enable-long-double
	make %{?_smp_mflags}
popd


%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
pushd double
	make install DESTDIR=${RPM_BUILD_ROOT}
	cp -a AUTHORS COPYING COPYRIGHT ChangeLog NEWS README* TODO ../
	cp -a doc/ ../
popd
pushd single
	make install DESTDIR=${RPM_BUILD_ROOT}
popd
pushd long
	make install DESTDIR=${RPM_BUILD_ROOT}
popd
rm -f ${RPM_BUILD_ROOT}%{_infodir}/dir


%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT


%post


%postun

%files
%doc AUTHORS COPYING COPYRIGHT ChangeLog NEWS README* TODO
%doc %{_mandir}/man?/*
%{_bindir}/*
%{_libdir}/*.so.*

%files devel
%doc doc/*.pdf doc/html/* doc/FAQ/fftw-faq.html/
%doc %{_infodir}/*.info*
%{_includedir}/*
%{_libdir}/pkgconfig/*
%{_libdir}/*.so

%files static
%exclude %{_libdir}/*.la
%{_libdir}/*.a


%changelog
* Mon Nov 30 2009 Dennis Gregorovic <dgregor@redhat.com> - 3.2.1-3.1
- Rebuilt for RHEL 6

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.2.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.2.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sat Feb 14 2009 Conrad Meyer <konrad@tylerc.org> - 3.2.1-1
- Bump to 3.2.1.

* Thu Dec 4 2008 Conrad Meyer <konrad@tylerc.org> - 3.2-1
- Bump to 3.2.

* Fri Jul 18 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 3.1.2-7
- fix license tag

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 3.1.2-6
- Autorebuild for GCC 4.3

* Fri Aug 24 2007 Quentin Spencer <qspencer@users.sf.net> 3.1.2-5
- Rebuild for F8.

* Fri Jul 27 2007 Quentin Spencer <qspencer@users.sf.net> 3.1.2-4
- Split static libs into separate package (bug 249686).

* Thu Oct 05 2006 Christian Iseli <Christian.Iseli@licr.org> 3.1.2-3
- rebuilt for unwind info generation, broken in gcc-4.1.1-21

* Tue Sep 26 2006 Quentin Spencer <qspencer@users.sf.net> 3.1.2-2
- BuildRequires: pkgconfig for -devel (bug 206444).

* Fri Sep  8 2006 Quentin Spencer <qspencer@users.sf.net> 3.1.2-1
- New release.

* Fri Jun  2 2006 Quentin Spencer <qspencer@users.sf.net> 3.1.1-1
- New upstream release.

* Fri Feb 24 2006 Quentin Spencer <qspencer@users.sf.net> 3.1-4
- Re-enable static libs (bug 181897).
- Build long-double version of libraries (bug 182587).

* Mon Feb 13 2006 Quentin Spencer <qspencer@users.sf.net> 3.1-3
- Add Obsoletes and Provides.

* Mon Feb 13 2006 Quentin Spencer <qspencer@users.sf.net> 3.1-2
- Rebuild for Fedora Extras 5.
- Disable static libs.
- Remove obsolete configure options.

* Wed Feb  1 2006 Quentin Spencer <qspencer@users.sf.net> 3.1-1
- Upgrade to the 3.x branch, incorporating changes from the fftw3 spec file.
- Add dist tag.

* Mon May 23 2005 Michael Schwendt <mschwendt[AT]users.sf.net> - 2.1.5-8
- BuildReq gcc-gfortran (#156490).

* Sun May 22 2005 Jeremy Katz <katzj@redhat.com> - 2.1.5-7
- rebuild on all arches
- buildrequire compat-gcc-32-g77

* Fri Apr  7 2005 Michael Schwendt <mschwendt[AT]users.sf.net>
- rebuilt

* Wed Nov 10 2004 Matthias Saou <http://freshrpms.net/> 2.1.5-5
- Bump release to provide Extras upgrade path.

* Tue Apr 06 2004 Phillip Compton <pcompton[AT]proteinmedia.com> - 0:2.1.5-0.fdr.4
- BuildReq gcc-g77.

* Mon Sep 22 2003 Phillip Compton <pcompton[AT]proteinmedia.com> - 0:2.1.5-0.fdr.3
- Dropped post/preun scripts for info.

* Wed Sep 17 2003 Phillip Compton <pcompton[AT]proteinmedia.com> - 0:2.1.5-0.fdr.2
- Remove aesthetic comments.
- buildroot -> RPM_BUILD_ROOT.
- post/preun for info files.

* Mon Apr 07 2003 Phillip Compton <pcompton[AT]proteinmedia.com> - 0:2.1.5-0.fdr.1
- Updated to 2.1.5.

* Tue Apr 01 2003 Phillip Compton <pcompton[AT]proteinmedia.com> - 0:2.1.4-0.fdr.2
- Added Epoch:0.
- Added ldconfig to post and postun.

* Sun Mar 22 2003 Phillip Compton <pcompton[AT]proteinmedia.com> - 2.1.4-0.fdr.1
- Updated to 2.1.4.

* Fri Mar 14 2003 Phillip Compton <pcompton[AT]proteinmedia.com> - 2.1.3-0.fdr.1
- Fedorafied.

* Mon Oct 21 2002 Matthias Saou <matthias.saou@est.une.marmotte.net>
- Initial RPM release.

