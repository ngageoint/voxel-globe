%include %{_sourcedir}/common.inc

Summary: PMVS is a multi-view stereo software that takes a set of images and camera parameters, then reconstructs 3D structure of an object or a scene visible in the images.
Name: pmvs
Version: 2.0
Release: 1%{?dist}
Group: Applications/Multimedia
License: GNU Public License (GPL)
URL: http://www.di.ens.fr/pmvs/
BuildRequires: lapack-devel, boost-devel, gsl-devel, libjpeg-turbo-devel, blas-devel
# The CMVS include the pmvs2 so if we don't them to overwrite each other we can not install booth of them.
Conflicts: cmvs
Source: pmvs-2-fix0.tar.gz
Source1: common.inc
Source2: clapack.tgz
BuildRoot:  %{_builddir}/%{name}-root
Packager: Attila Zsolt Sajo

%description
PMVS is a multi-view stereo software that takes a set of images and camera parameters, then reconstructs 3D structure of an object or a scene visible in the images. Only rigid structure is reconstructed, in other words, the software automatically ignores non-rigid objects such as pedestrians in front of a building. The software outputs a set of oriented points instead of a polygonal (or a mesh) model, where both the 3D coordinate and the surface normal are estimated at each oriented point. This is the second version of the software (a link to the first version with a gallery) distributed under GPL. The software is 64-bit compatible.

PMVS2 was developped when Yasutaka Furukawa was a graduate student at University of Illinois at Urbana-Champaign under the supervision of Prof. Jean Ponce, who was affiliated with University of Illinois at Urbana-Champaign and Ecole Normale SupÃ©rieure. Further modifications and enhancements were added when Yasutaka Furukawa was a postdoc at University of Washington. 

%prep
%setup -q -n pmvs-2/program/main
tar -zxf %{SOURCE2} 
mv CLAPACK-*/INCLUDE clapack
sed -i 's@-llapack@-ltatlas@g' Makefile

%build
make YOURINCLUDEPATH="-I. -I%{install_dir}%{_includedir}" YOURLDLIBPATH=-L%{install_dir}%{_libdir}

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

mkdir -p %{buildroot}%{_bindir}/
install -m 755 pmvs2 %{buildroot}%{_bindir}

%clean

%files
%{_bindir}/pmvs2

%changelog
* Thu Oct 30 2014  Attila Zsolt Sajo <sajozsattila@gmail.com>
- Original spec file wroted