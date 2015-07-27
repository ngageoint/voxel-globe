%include %{_sourcedir}/common.inc

Name:           opencv
Version:        3.0.0
Release:        1%{?dist}
Summary:        Collection of algorithms for computer vision

Group:          Development/Libraries
# This is normal three clause BSD.
License:        BSD
URL:            http://opencv.willowgarage.com/wiki/
Source0:        %{name}-%{version}-rc1.zip
Source1:        common.inc
Source2:        ippicv_linux_20141027.tgz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  libtool
BuildRequires:  cmake >= 2.4

BuildRequires:  gtk2-devel
# make this package buildable on Fedora 12 and later
%if 0%{?fedora} >= 12 
BuildRequires: libunicapgtk-devel
%else
BuildRequires:  unicap-devel
%endif
BuildRequires:  libtheora-devel
BuildRequires:  libvorbis-devel
%ifnarch s390 s390x
BuildRequires:  libraw1394-devel
BuildRequires:  libdc1394-devel
%endif
BuildRequires:  libpng-devel
BuildRequires:  libjpeg-devel
BuildRequires:  libtiff-devel
BuildRequires:  libtool
BuildRequires:  zlib-devel, pkgconfig
BuildRequires:  python-devel
BuildRequires:  python-imaging, numpy, swig >= 1.3.24

%description
OpenCV means Intel® Open Source Computer Vision Library. It is a collection of
C functions and a few C++ classes that implement some popular Image Processing
and Computer Vision algorithms.


%package devel
Summary:        Development files for using the OpenCV library
Group:          Development/Libraries
Requires:       opencv = %{version}-%{release}
Requires:       pkgconfig

%description devel
This package contains the OpenCV C/C++ library and header files, as well as
documentation. It should be installed if you want to develop programs that
will use the OpenCV library. You should consider installing opencv-devel-docs
package.

%package devel-docs
Summary:        Development files for using the OpenCV library
Group:          Development/Libraries
Requires:       opencv-devel = %{version}-%{release}
Requires:       pkgconfig
BuildArch:      noarch

%description devel-docs
This package contains the OpenCV documentation and examples programs.

%package python
Summary:        Python bindings for apps which use OpenCV
Group:          Development/Libraries
Requires:       opencv = %{version}-%{release}
Requires:       python-imaging
Requires:       numpy

%description python
This package contains Python bindings for the OpenCV library.

%prep
%setup -q -n %{name}-%{version}-rc1

%build

%ifarch i386
export CXXFLAGS="%{__global_cflags} -m32 -fasynchronous-unwind-tables"
%endif

mkdir build
pushd build

export PYTHON2_LIBRARY=%{install_dir}%{_libdir}/libpython2.7.so
export PYTHON2_INCLUDE_DIR=%{install_dir}%{_includedir}/python2.7
export PYTHON2_EXECUTABLE=%{_roamdir}/python

export OPENCV_ICV_URL=file://$(dirname %{SOURCE2})
#Redirect download to local file

%{__cmake} -DCMAKE_VERBOSE_MAKEFILE=ON \
      -DCMAKE_INSTALL_LIBDIR:PATH=%{_libdir} \
      -G "Unix Makefiles" \
      -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_INSTALL_PREFIX:PATH=%{_prefix} \
      -DINCLUDE_INSTALL_DIR:PATH=%{_includedir} \
      -DSYSCONF_INSTALL_DIR:PATH=%{_sysconfdir} \
      -DSHARE_INSTALL_PREFIX:PATH=%{_datadir} \
      -DBUILD_SWIG_PYTHON_SUPPORT=1 \
      -DINSTALL_C_EXAMPLES=1 \
      -DINSTALL_PYTHON_EXAMPLES=1 \
      -DWITH_FFMPEG=OFF \
      -DBUILD_opencv_java=OFF \
      -DCUDA_GENERATION=Auto \
      -DPYTHON_INCLUDE_DIR2=${PYTHON2_INCLUDE_DIR} \
      -DENABLE_OPENMP=1\
      ..
#-DPYTHON_INCLUDE_DIR2 is for some stupid error in cmake 2.8.11 where it won't 
#find DIR2, OF COURSE, and then FAIL! It's looking for pyconfig.h... dumbass cmake

make VERBOSE=1 %{?_smp_mflags} DESTDIR="%{buildroot}"
popd

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
pushd build

mkdir -p "$RPM_BUILD_ROOT%{_libdir}"
mkdir -p "$RPM_BUILD_ROOT%{_bindir}"
mkdir -p "$RPM_BUILD_ROOT%{_includedir}"

#Fix an ANNOYING bug in opencv cmake configuration. They actually CREATE
#dependencies DURING built, .depend files, so when the cmake integrity
#checker checks the integrity, IT ALWAYS FAILS, and now has to rerun,
#cmake WITHOUT all the fancy -D options that... oh, I dunno, MAKE THINGS
#WORK! And then rebuild, which just ends disastourously... I don't know
#enough about cmake to fix the problem, but if I just reset all the
#timestamps, the problem goes away. This is a CUDA only problem due to
#FindCUDA.cmake

#Makefile CMakeFiles/cmake.check_cache are the time refernce files. I
#want which ever is oldest
REF_FILE=Makefile
if [ "Makefile" -nt "CMakeFiles/cmake.check_cache" ]; then
  REF_FILE=CMakeFiles/cmake.check_cache
fi

find modules -name '*.cu.o.depend' -exec touch -r ${REF_FILE} {} \;

make install DESTDIR=$RPM_BUILD_ROOT INSTALL="install -p" CPPROG="cp -p"

rm -f $RPM_BUILD_ROOT%{_datadir}/%{name}/samples/c/build_all.sh \
      $RPM_BUILD_ROOT%{_datadir}/%{name}/samples/c/cvsample.dsp \
      $RPM_BUILD_ROOT%{_datadir}/%{name}/samples/c/cvsample.vcproj \
      $RPM_BUILD_ROOT%{_datadir}/%{name}/samples/c/facedetect.cmd

install -m644 cvconfig.h $RPM_BUILD_ROOT%{_includedir}/%{name}/cvconfig.h
mkdir -p $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/
# install documentation
#install -m644 doc/%{name}.pdf $RPM_BUILD_ROOT%{_docdir}/%{name}-doc-%{version}/%{name}.pdf
install -m644 ../doc/*.{html,png,jpg} $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}/

# fix dos end of lines
#sed -i 's|\r||g'  $RPM_BUILD_ROOT/%{_datadir}/%{name}/samples/c/adaptiveskindetector.cpp
# remove unnecessary documentation
rm -rf $RPM_BUILD_ROOT%{_datadir}/opencv/{doc/,samples/octave/}

# Fix nonstandard executable permissions
#chmod 0755 $RPM_BUILD_ROOT%{_datadir}/opencv/samples/python2/*.py
chmod 0755 $RPM_BUILD_ROOT%{python_sitearch}/cv2.so
#chmod 0755 $RPM_BUILD_ROOT%{python_sitearch}/opencv/*.so

mkdir -p $RPM_BUILD_ROOT%{_datadir}/OpenCV/samples/python2
install -m644 ../samples/python2/* $RPM_BUILD_ROOT%{_datadir}/OpenCV/samples/python2/

popd

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%{_bindir}/opencv_*
%{_libdir}/lib*.so.*
%{_libdir}/libopencv_*.a
%dir %{_datadir}/OpenCV
%{_datadir}/OpenCV/lbpcascades
%{_datadir}/OpenCV/haarcascades
%{_datadir}/OpenCV/3rdparty/lib/libippicv.a

%files devel
%defattr(-,root,root,-)
%{_includedir}/opencv
%{_includedir}/opencv2
%{_libdir}/lib*.so
%{_libdir}/pkgconfig/opencv.pc
%{_datadir}/OpenCV/*.cmake

%files devel-docs
%defattr(-,root,root,-)
%doc %{_datadir}/doc/opencv-3.0.0/
%doc %dir %{_datadir}/OpenCV/samples
%doc %{_datadir}/OpenCV/samples/cpp
%doc %{_datadir}/OpenCV/samples/gpu
%doc %{_datadir}/OpenCV/samples/tapi

%files python
%defattr(-,root,root,-)
%{python_sitearch}/cv2.so
%doc %{_datadir}/OpenCV/samples/python2

%changelog
* Mon Jun  3 2013 Honza Horak <hhorak@redhat.com> - 2.0.0-12
- Move cmake file to libdir to solve multilib issues
  Resolves: #658060

* Tue Jun  8 2010 Karel Klic <kklic@redhat.com> - 2.0.0-9
- Fix malformed XMLs
  Resolves: #594290

* Tue Apr 13 2010 Karel Klic <kklic@redhat.com> - 2.0.0-8
- Fix nonstandard executable permissions
- Make the spec file compilable on Fedora 12

* Mon Mar 08 2010 Karel Klic <kklic@redhat.com> - 2.0.0-7
- re-enable testing on CMake build system
- fix memory corruption in the gaussian random number generator

* Thu Feb 25 2010 Haïkel Guémar <karlthered@gmail.com> - 2.0.0-6
- use cmake build system
- applications renamed to opencv_xxx instead of opencv-xxx
- add devel-docs subpackage #546605
- add OpenCVConfig.cmake
- enable openmp build
- enable old SWIG based python wrappers
- opencv package is a good boy and use global instead of define

* Tue Feb 16 2010 Karel Klic <kklic@redhat.com> - 2.0.0-5
- Set CXXFLAXS without -match=i386 for i386 architecture #565074

* Sat Jan 09 2010 Rakesh Pandit <rakesh@fedoraproject.org> - 2.0.0-4
- Updated opencv-samples-Makefile (Thanks Scott Tsai) #553697

* Wed Jan 06 2010 Karel Klic <kklic@redhat.com> - 2.0.0-3
- Fixed spec file issues detected by rpmlint

* Sun Dec 06 2009 Haïkel Guémar <karlthered@gmail.com> - 2.0.0-2
- Fix autotools scripts (missing LBP features) - #544167

* Fri Nov 27 2009 Haïkel Guémar <karlthered@gmail.com> - 2.0.0-1
- Updated to 2.0.0
- Removed upstream-ed patches
- Ugly hack (added cvconfig.h)
- Disable %%check on ppc64

* Thu Sep 10 2009 Karsten Hopp <karsten@redhat.com> - 1.1.0-0.7.pre1
- fix build on s390x where we don't have libraw1394 and devel

* Fri Jul 30 2009 Haïkel Guémar <karlthered@gmail.com> - 1.1.0.0.6.pre1
- Fix typo I introduced that prevented build on i386/i586

* Fri Jul 30 2009 Haïkel Guémar <karlthered@gmail.com> - 1.1.0.0.5.pre1
- Added 1394 libs and unicap support

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.0-0.4.pre1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Jul 16 2009 kwizart < kwizart at gmail.com > - 1.1.0-0.3.pre1
- Build with gstreamer support - #491223
- Backport gcc43 fix from trunk

* Thu Jul 16 2009 kwizart < kwizart at gmail.com > - 1.1.0-0.2.pre1
- Fix FTBFS #511705

* Fri Apr 24 2009 kwizart < kwizart at gmail.com > - 1.1.0-0.1.pre1
- Update to 1.1pre1
- Disable CXXFLAGS hardcoded optimization
- Add BR: python-imaging, numpy
- Disable make check failure for now

* Wed Apr 22 2009 kwizart < kwizart at gmail.com > - 1.0.0-14
- Fix for gcc44
- Enable BR jasper-devel
- Disable ldconfig run on python modules (uneeded)
- Prevent timestamp change on install

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.0-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Dec 29 2008 Rakesh Pandit <rakesh@fedoraproject.org> - 1.0.0-12
- fix URL field

* Fri Dec 19 2008 Ralf Corsépius <corsepiu@fedoraproject.org> - 1.0.0-11
- Adopt latest python spec rules.
- Rebuild for Python 2.6 once again.

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 1.0.0-10
- Rebuild for Python 2.6

* Thu May 22 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 1.0.0-9
- fix license tag

* Sun May 11 2008 Ralf Corsépius <rc040203@freenet.de> - 1.0.0-8
- Adjust library order in opencv.pc.in (BZ 445937).

* Mon Feb 18 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 1.0.0-7
- Autorebuild for GCC 4.3

* Sun Feb 10 2008 Ralf Corsépius <rc040203@freenet.de> - 1.0.0-6
- Rebuild for gcc43.

* Tue Aug 28 2007 Fedora Release Engineering <rel-eng at fedoraproject dot org> - 1.0.0-5
- Rebuild for selinux ppc32 issue.

* Wed Aug 22 2007 Ralf Corsépius <rc040203@freenet.de> - 1.0.0-4
- Mass rebuild.

* Thu Mar 22 2007 Ralf Corsépius <rc040203@freenet.de> - 1.0.0-3
- Fix %%{_datadir}/opencv/samples ownership.
- Adjust timestamp of cvconfig.h.in to avoid re-running autoheader.

* Thu Mar 22 2007 Ralf Corsépius <rc040203@freenet.de> - 1.0.0-2
- Move all of the python module to pyexecdir (BZ 233128).
- Activate the testsuite.

* Mon Dec 11 2006 Ralf Corsépius <rc040203@freenet.de> - 1.0.0-1
- Upstream update.

* Mon Dec 11 2006 Ralf Corsépius <rc040203@freenet.de> - 0.9.9-4
- Remove python-abi.

* Thu Oct 05 2006 Christian Iseli <Christian.Iseli@licr.org> 0.9.9-3
- rebuilt for unwind info generation, broken in gcc-4.1.1-21

* Thu Sep 21 2006 Ralf Corsépius <rc040203@freenet.de> - 0.9.9-2
- Stop configure.in from hacking CXXFLAGS.
- Activate testsuite.
- Let *-devel require pkgconfig.

* Thu Sep 21 2006 Ralf Corsépius <rc040203@freenet.de> - 0.9.9-1
- Upstream update.
- Don't BR: autotools.
- Install samples' Makefile as GNUmakefile.

* Thu Sep 21 2006 Ralf Corsépius <rc040203@freenet.de> - 0.9.7-18
- Un'%%ghost *.pyo.
- Separate %%{pythondir} from %%{pyexecdir}.

* Thu Sep 21 2006 Ralf Corsépius <rc040203@freenet.de> - 0.9.7-17
- Rebuild for FC6.
- BR: libtool.

* Fri Mar 17 2006 Simon Perreault <nomis80@nomis80.org> - 0.9.7-16
- Rebuild.

* Wed Mar  8 2006 Simon Perreault <nomis80@nomis80.org> - 0.9.7-15
- Force a re-run of Autotools by calling autoreconf.

* Wed Mar  8 2006 Simon Perreault <nomis80@nomis80.org> - 0.9.7-14
- Added build dependency on Autotools.

* Tue Mar  7 2006 Simon Perreault <nomis80@nomis80.org> - 0.9.7-13
- Changed intrinsics patch so that it matches upstream.

* Tue Mar  7 2006 Simon Perreault <nomis80@nomis80.org> - 0.9.7-12
- More intrinsics patch fixing.

* Tue Mar  7 2006 Simon Perreault <nomis80@nomis80.org> - 0.9.7-11
- Don't do "make check" because it doesn't run any tests anyway.
- Back to main intrinsics patch.

* Tue Mar  7 2006 Simon Perreault <nomis80@nomis80.org> - 0.9.7-10
- Using simple intrinsincs patch.

* Tue Mar  7 2006 Simon Perreault <nomis80@nomis80.org> - 0.9.7-9
- Still more fixing of intrinsics patch for Python bindings on x86_64.

* Tue Mar  7 2006 Simon Perreault <nomis80@nomis80.org> - 0.9.7-8
- Again fixed intrinsics patch so that Python modules build on x86_64.

* Tue Mar  7 2006 Simon Perreault <nomis80@nomis80.org> - 0.9.7-7
- Fixed intrinsics patch so that it works.

* Tue Mar  7 2006 Simon Perreault <nomis80@nomis80.org> - 0.9.7-6
- Fixed Python bindings location on x86_64.

* Mon Mar  6 2006 Simon Perreault <nomis80@nomis80.org> - 0.9.7-5
- SSE2 support on x86_64.

* Mon Mar  6 2006 Simon Perreault <nomis80@nomis80.org> - 0.9.7-4
- Rebuild

* Sun Oct 16 2005 Simon Perreault <nomis80@nomis80.org> - 0.9.7-3
- Removed useless sample compilation makefiles/project files and replaced them
  with one that works on Fedora Core.
- Removed shellbang from Python modules.

* Mon Oct 10 2005 Simon Perreault <nomis80@nomis80.org> - 0.9.7-2
- Made FFMPEG dependency optional (needs to be disabled for inclusion in FE).

* Mon Oct 10 2005 Simon Perreault <nomis80@nomis80.org> - 0.9.7-1
- Initial package.
