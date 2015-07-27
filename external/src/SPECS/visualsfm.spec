%include %{_sourcedir}/common.inc

Name: visualsfm		
Version: 0.5.26
Release:	3%{?dist}
Summary: VisualSFM is a GUI application for 3D reconstruction using structure from motion (SFM).	
Group:	Applications/Multimedia
License: Copyright 2006-2012 Changchang Wu
URL:	http://ccwu.me/vsfm/
Requires: siftgpu, cmvs, graclus, xorg-x11-fonts-Type1, gtk2
BuildRequires: siftgpu, cmvs, graclus, gtk2-devel
%ifarch i686	
Source0: %{name}-%{version}-i686.zip
%else
Source0: %{name}-%{version}-x86_64.zip
%endif
Source1: common.inc
Packager:  Attila Zsolt Sajo

%description
VisualSFM is a GUI application for 3D reconstruction using structure from motion (SFM). The reconstruction system integrates several of my previous projects: SIFT on GPU(SiftGPU), Multicore Bundle Adjustment, and Towards Linear-time Incremental Structure from Motion. VisualSFM runs fast by exploiting multicore parallelism for feature detection, feature matching, and bundle adjustment.
For dense reconstruction, this program supports Yasutaka Furukawa's PMVS/CMVS tool chain, and can prepare data for Michal Jancosek's CMP-MVS. In addition, the output of VisualSFM is natively supported by Mathias Rothermel and Konrad Wenzel's SURE. 

%prep
%setup -n vsfm

%build
make

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

mkdir -p %{buildroot}%{_bindir}
install -m 755 bin/VisualSFM  %{buildroot}%{_bindir}/visualsfm
###install -m 755 bin/VisualSFM  %{buildroot}%{_bindir}
###echo '#!/bin/bash
###BASE_DIR=$(dirname ${BASH_SOURCE[0]})
###export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/usr/local/cuda/lib64
###exec ${BASE_DIR}/VisualSFM "${@}"' > %{buildroot}%{_bindir}/visualsfm
###chmod 755 %{buildroot}%{_bindir}/visualsfm

mkdir -p %{buildroot}%{_localstatedir}/visualsfm
ln -s %{prefix_bin_rel}/%{localstate_prefix_rel}/visualsfm %{buildroot}%{_bindir}/log

%files
%{_bindir}/visualsfm
###%{_bindir}/VisualSFM
%{_bindir}/log
%{_localstatedir}/visualsfm
#/var/log/visualsfm

%changelog
* Thu Oct 30 2014  Attila Zsolt Sajo <sajozsattila@gmail.com>
- Original spec file wroted
- Known problem: regular user can not write log files
