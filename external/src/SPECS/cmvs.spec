%include %{_sourcedir}/common.inc

Summary: The CMVS takes the output of a structure-from-motion (SfM) software as input, then decomposes the input images into a set of image clusters of managable size. 
Name: cmvs
Version: 2.0
Release: 1%{?dist}
Group: Applications/Multimedia
License: GNU Public License (GPL)
URL: http://www.di.ens.fr/cmvs/
Source: cmvs-fix2.tar.gz
Source1: common.inc
Source2: clapack.tgz
BuildRoot:  %{_builddir}/%{name}-root
BuildRequires: lapack-devel, boost-devel, gsl-devel, libjpeg-turbo-devel, blas-devel
# The CMVS include the pmvs2 so if we don't them to overwrite each other we can not install booth of them.
Conflicts: pmvs2
Packager: Attila Zsolt Sajo

%description
Many multi-view stereo (MVS) algorithms do not scale well to a large number of input images (lack of computational and memory resources). This software (CMVS) takes the output of a structure-from-motion (SfM) software as input, then decomposes the input images into a set of image clusters of managable size. An MVS software can be used to process each cluster independently and in parallel, where the union of reconstructions from all the clusters should not miss any details that can be otherwise obtained from the whole image set. CMVS should be used in conjunction with an SfM software Bundler and an MVS software PMVS2.

%prep
%setup -q -n cmvs/program/main/

tar -zxf %{SOURCE2} 
mv CLAPACK-*/INCLUDE clapack

sed -i 's@\(^Your .*$\)@#\1@' Makefile
sed -i 's@-llapack@-ltatlas@' Makefile
sed -i '1i #include <vector>\n#include <numeric>' ../base/cmvs/bundle.cc
sed -i '1i #include <stdlib.h>' genOption.cc

%build
make YOUR_INCLUDE_PATH="-I. -I%{install_dir}%{_includedir} -I%{install_dir}%{_includedir}/metisLib" YOUR_LDLIB_PATH=-L%{install_dir}%{_libdir}

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

mkdir -p %{buildroot}%{_bindir}/
install -m 755 cmvs %{buildroot}%{_bindir}
install -m 755 genOption %{buildroot}%{_bindir}
install -m 755 pmvs2 %{buildroot}%{_bindir}/cmvs_pmvs2

%files
%{_bindir}/genOption
%{_bindir}/cmvs
%{_bindir}/cmvs_pmvs2

%changelog
* Thu Oct 30 2014  Attila Zsolt Sajo <sajozsattila@gmail.com>
- Original spec file wroted