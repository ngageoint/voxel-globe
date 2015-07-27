%include %{_sourcedir}/common.inc

Name:		scipy
Version:	0.15.1
Release:	1%{?dist}
Summary:	Scientific Tools for Python
Source:		%{name}-%{version}.tar.gz
Source1:        common.inc

License:	BSD and Boost and Public Domain
Group:		Development/Libraries
URL: 		http://www.scipy.org
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root

BuildRequires:  numpy, python-devel,f2py
BuildRequires:  fftw-devel, blas-devel, lapack-devel, suitesparse-devel
BuildRequires:  gcc-gfortran, swig
Requires:       numpy, python,f2py

%description
Scipy is open-source software for mathematics, science, and
engineering. The core library is NumPy which provides convenient and
fast N-dimensional array manipulation. The SciPy library is built to
work with NumPy arrays, and provides many user-friendly and efficient
numerical routines such as routines for numerical integration and
optimization. Together, they run on all popular operating systems, are
quick to install, and are free of charge. NumPy and SciPy are easy to
use, but powerful enough to be depended upon by some of the world's
leading scientists and engineers.


%prep
%setup -q -n %{name}-%{version}

cat > site.cfg << EOF

[amd]
library_dirs = %{install_dir}%{_libdir}
include_dirs = %{install_dir}%{_libdir}
amd_libs = amd

[umfpack]
library_dirs = %{install_dir}%{_libdir}
include_dirs = %{install_dir}%{_includedir}
umfpack_libs = umfpack
EOF

sed -i s/'uses_mkl(info) and sys.platform == "darwin"'/'sys.platform == "darwin" and uses_mkl(info)'/ ./scipy/_build_utils/_fortran.py

%build
env CFLAGS="$RPM_OPT_FLAGS" \
    FFTW=%{install_dir}%{_libdir} \
    BLAS=%{install_dir}%{_libdir} \
    LAPACK=%{install_dir}%{_libdir} \
    ATLAS=%{install_dir}%{_libdir} \
    %{__python} setup.py config_fc --fcompiler=gnu95 --noarch build

%check
mkdir test
cd test
PYTHONPATH=$RPM_BUILD_ROOT%{python_sitearch} %{__python} -c "import scipy; scipy.test('full')"

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
env CFLAGS="$RPM_OPT_FLAGS" \
    FFTW=%{install_dir}%{_libdir} \
    BLAS=%{install_dir}%{_libdir} \
    LAPACK=%{install_dir}%{_libdir} \
    ATLAS=%{install_dir}%{_libdir} \
    %{__python} setup.py install --prefix=${RPM_BUILD_ROOT}%{cat_prefix} --install-data=${RPM_BUILD_ROOT}%{_datadir}

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%exclude /usr/lib/debug
/

%post

%postun

%changelog
* Sat May 10 2014 Orion Poplawski <orion@cora.nwra.com> - 0.14-2
- Rebuild with Python 3.4

* Tue May  6 2014 Orion Poplawski <orion@cora.nwra.com> - 0.14-1
- Update to 0.14
- Do not use system python-six (bug #1046817)

* Thu Feb 20 2014 Thomas Spura <tomspur@fedoraproject.org> - 0.13.3-2
- use python2 macros everywhere (Requested by Han Boetes)

* Tue Feb  4 2014 Thomas Spura <tomspur@fedoraproject.org> - 0.13.3-1
- Update to 0.13.3

* Mon Dec 9 2013 Orion Poplwski <orion@cora.nwra.com> - 0.13.2-1
- Update to 0.13.2

* Fri Dec 06 2013 Nils Philippsen <nils@redhat.com> - 0.13.1-2
- rebuild (suitesparse)

* Sun Nov 17 2013 Orion Poplwski <orion@cora.nwra.com> - 0.13.1-1
- Update to 0.13.1

* Wed Oct 23 2013 Tomas Tomecek <ttomecek@redhat.com> - 0.13.0-2
- Update to 0.13.0 final

* Tue Oct 15 2013 Orion Poplwski <orion@cora.nwra.com> - 0.13.0-0.4.rc1
- Update to 0.13.0rc1

* Tue Oct 01 2013 Tomas Tomecek <ttomecek@redhat.com> - 0.13.0-0.3.b1
- rebuilt with atlas 3.10

* Mon Sep 9 2013 Orion Poplwski <orion@cora.nwra.com> - 0.13.0-0.2.b1
- Unbundle python-six (bug #1005350)

* Thu Aug 29 2013 Orion Poplwski <orion@cora.nwra.com> - 0.13.0-0.1.b1
- Update to 0.13.0b1
- Drop patches applied upstream
- Fixup changelog and summary

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.12.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Tue Jul 30 2013 Tomas Tomecek <ttomecek@redhat.com> - 0.12.0-4
- Fix rpmlint warnings
- License update
- Add patch to use build_dir argument in build_extension

* Wed May 15 2013 Orion Poplawski <orion@cora.nwra.com> - 0.12.0-3
- Remove old ufsparse references, use suitesparse
- Spec cleanup

* Mon Apr 15 2013 Orion Poplawski <orion@cora.nwra.com> - 0.12.0-2
- Add patch to fix segfaul in test of sgeqrf

* Wed Apr 10 2013 Orion Poplawski <orion@cora.nwra.com> - 0.12.0-1
- Update to 0.12.0 final
- No longer remove weave from python3 build

* Sat Feb 16 2013 Orion Poplawski <orion@cora.nwra.com> - 0.12.0-0.1.b1
- Update to 0.12.0b1
- Drop upstreamed linalg patch

* Wed Feb 13 2013 Orion Poplawski <orion@cora.nwra.com> - 0.11.0-4
- Add patch from upstream to fix python3.3 issues in linalg routines

* Tue Feb 12 2013 Orion Poplawski <orion@cora.nwra.com> - 0.11.0-3
- Disable python3 tests for now

* Mon Oct  8 2012 Orion Poplawski <orion@cora.nwra.com> - 0.11.0-2
- Add requires python3-numpy, python3-f2py for python3-scipy (bug 863755)

* Sun Sep 30 2012 Orion Poplawski <orion@cora.nwra.com> - 0.11.0-1
- Update to 0.11.0 final

* Thu Aug 23 2012 Orion Poplawski <orion@cora.nwra.com> - 0.11.0-0.1.rc2
- Update to 0.11.0rc2

* Mon Aug  6 2012 Orion Poplawski <orion@cora.nwra.com> - 0.10.1-4
- Rebuild for python 3.3

* Fri Aug  3 2012 David Malcolm <dmalcolm@redhat.com> - 0.10.1-3
- remove rhel logic from with_python3 conditional

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.10.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Mar 16 2012 Orion Poplawski <orion@cora.nwra.com> - 0.10.1-1
- Update to 0.10.1

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.10.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Mon Nov 14 2011 Orion Poplawski <orion@cora.nwra.com> - 0.10.0-1
- Update to 0.10.0

* Sat Sep  3 2011 Thomas Spura <tomspur@fedoraproject.org> - 0.9.0-2
- little cosmetic changes
- filter provides in python_sitearch

* Fri Sep 02 2011 Andrew McNabb <amcnabb@mcnabbs.org>
- add python3 subpackage

* Fri Apr 1 2011 Orion Poplawski <orion@cora.nwra.com> - 0.9.0-1
- Update to 0.9.0
- Drop all stsci sources and patches, dropped from upstream
- Drop gcc and py27 patches fixed upstream
- Add %%check section to run tests

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sat Jul 31 2010 Toshio Kuratomi <toshio@fedoraproject.org> - 0.7.2-3
- Fix scipy build on python-2.7

* Thu Jul 22 2010 David Malcolm <dmalcolm@redhat.com> - 0.7.2-2
- Rebuilt for https://fedoraproject.org/wiki/Features/Python_2.7/MassRebuild

* Thu Jul 1 2010 Jef Spaleta <jspaleta@fedoraproject.org> - 0.7.2-1
- New upstream release

* Sun Apr 11 2010 Jef Spaleta <jspaleta@fedoraproject.org> - 0.7.1-3
- Bump for rebuild against numpy 1.3

* Thu Apr  1 2010 Jef Spaleta <jspaleta@fedoraproject.org> - 0.7.1-2
- Bump for rebuild against numpy 1.4.0

* Thu Dec 10 2009 Jon Ciesla <limb@jcomserv.net> - 0.7.1-1
- Update to 0.7.1.

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Sun Jun 14  2009 Jef Spaleta <jspaleta@fedoraproject.org> - 0.7.0-4
- Fix for gcc34 weave blitz bug #505379

* Tue Apr 7  2009 Jef Spaleta <jspaleta@fedoraproject.org> - 0.7.0-3
- Add f2py requires to prepared for numpy packaging split

* Sun Mar 1  2009 Jef Spaleta <jspaleta@fedoraproject.org> - 0.7.0-2
- Patch for stsci image function syntax fix.

* Thu Feb 26 2009 Jef Spaleta <jspaleta@fedoraproject.org> - 0.7.0-1
- Update to final 0.7 release

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7.0-0.3.b1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Dec 15 2008 Deji Akingunola <dakingun@gmail.com> - 0.7.0-0.2.b1
- Rebuild for atlas-3.8.2

* Mon Dec 01 2008  Jef Spaleta <jspaleta@fedoraproject.org> - 0.7.0-0.1.b1
- Update to latest beta which lists python 2.6 support

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 0.6.0-8
- Rebuild for Python 2.6

* Fri Oct 03 2008 Jef Spaleta <jspaleta@fedoraproject.org> - 0.6.0-7
- fix the stsci fix

* Thu Oct 02 2008 Jef Spaleta <jspaleta@fedoraproject.org> - 0.6.0-6
- include missing setup files for stsci module

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 0.6.0-5
- Autorebuild for GCC 4.3

* Fri Jan 04 2008 Jef Spaleta <jspaleta@fedoraproject.org> - 0.6.0-4
- fix for egg-info file creation

* Wed Oct 03 2007 Jef Spaleta <jspaleta@gmail.com> - 0.6.0-3
- include_dirs changes for ufsparse change in development

* Tue Oct 02 2007 Jef Spaleta <jspaleta@gmail.com> - 0.6.0-2
- Fix licensing to match Fedora packaging guidance
- Remove unnecessary library deps

* Tue Sep 25 2007 Jarrod Millman <millman@berkeley.edu> - 0.6.0-1
- update to new upstream source
- update Summary, License, Url, and description
- added extra dependencies
- remove symlink since Lib has been renamed scipy

* Tue Aug 21 2007 Jef Spaleta <jspaleta@gmail.com> - 0.5.2.1-1
- Update to new upstream source

* Tue Aug 21 2007 Jef Spaleta <jspaleta@gmail.com> - 0.5.2-3
- fix licensing tag and bump for buildid rebuild

* Wed Apr 18 2007 Jef Spaleta <jspaleta@gmail.com> - 0.5.2-2.2
- go back to using gfortran now that numpy is patched

* Sat Apr 14 2007 Jef Spaleta <jspaleta@gmail.com> - 0.5.2-2.1
- minor correction for f77 usage

* Sat Apr 14 2007 Jef Spaleta <jspaleta@gmail.com> - 0.5.2-2
- revert to f77 due to issue with numpy in development

* Sat Apr 14 2007 Jef Spaleta <jspaleta@gmail.com> - 0.5.2-1.1
- remove arch specific optimizations

* Wed Feb 21 2007 Jef Spaleta <jspaleta@gmail.com> - 0.5.2-1
- Update for new upstream release

* Mon Dec  11 2006 Jef Spaleta <jspaleta@gmail.com> - 0.5.1-5
- Bump for rebuild against python 2.5 in devel tree

* Sun Dec  3 2006 Jef Spaleta <jspaleta@gmail.com> - 0.5.1-4
- Minor adjustments to specfile for packaging guidelines.
- Changed buildrequires fftw version 3  from fftw2

* Sat Dec  2 2006 Jef Spaleta <jspaleta@gmail.com> - 0.5.1-2
- Updated spec for FE Packaging Guidelines and for upstream version 0.5.1

* Mon May  8 2006 Neal Becker <ndbecker2@gmail.com> - 0.4.8-4
- Add BuildRequires gcc-c++
- Add python-devel
- Add libstdc++

* Mon May  8 2006 Neal Becker <ndbecker2@gmail.com> - 0.4.8-3
- Add BuildRequires gcc-gfortran

* Sun May  7 2006 Neal Becker <ndbecker2@gmail.com> - 0.4.8-3
- Add BuildRequires numpy


* Wed May  3 2006 Neal Becker <ndbecker2@gmail.com> - 0.4.8-2
- Fix BuildRoot
- Add BuildRequires, Requires
- Test remove d1mach patch
- Fix defattr
- Add changelog
- Removed Prefix, Vendor
- Fix Source0

#%changelog

