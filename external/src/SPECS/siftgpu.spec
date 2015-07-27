%include %{_sourcedir}/common.inc

Summary: SiftGPU is an implementation of SIFT for GPU. SiftGPU processes pixels parallely to build Gaussian pyramids and detect DoG Keypoints.
Name: siftgpu
Version: 400
Release: 1%{?dist}
Group: Applications/Multimedia
License: Educational, Research and Non-profit purposes
URL: http://cs.unc.edu/~ccwu/siftgpu/download.html
Source: SiftGPU-V%{version}.zip
Source1: common.inc
Requires: freeglut-devel glew-devel DevIL-devel
BuildRoot:  %{_builddir}/%{name}-root
Packager: Sajo Zsolt Attila

%package        devel
Summary:	Development files for siftgpu
Group:		Development/Libraries
Requires: 	%{name} = %{version}-%{release}


%description
SiftGPU is an implementation of SIFT [1] for GPU. SiftGPU processes pixels parallely to build Gaussian pyramids and detect DoG Keypoints. Based on GPU list generation[3], SiftGPU then uses a GPU/CPU mixed method to efficiently build compact keypoint lists. Finally keypoints are processed parallely to get their orientations and descriptors.

SiftGPU is inspired by Andrea Vedaldi's sift++ and Sudipta N Sinha et al's GPU-SIFT.

SiftGPU also includes a GPU exhaustive/guided sift matcher SiftMatchGPU. It basically multiplies the descriptor matrix on GPU and finds the closest feature matches on GPU. Both GLSL and CUDA implementations are provided. 

%description devel
The %{name}-devel package contains development files for %{name}.

%prep
%setup -n SiftGPU

sed -i 's|\(LIBS_SIFTGPU.*-lcudart\)|\1 -Wl,-rpath=$(CUDA_INSTALL_PATH)/lib64 |' makefile
# Add rpath for cuda to make running easier

sed -i 's@\(-o $(BIN_DIR).*CFLAGS)\)@\1 -L%{install_dir}%{_libdir}@' makefile  
# Add VIP LIB dir so it links

%build
%if 0%{?ubuntu} || 0%{?mint}
CUDA_INSTALL_PATH=/usr
%else
CUDA_INSTALL_PATH=/usr/local/cuda
%endif
make CUDA_INSTALL_PATH=${CUDA_INSTALL_PATH}

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

mkdir -p %{buildroot}%{_libdir}
install -m 644 bin/libsiftgpu.so %{buildroot}%{_libdir}/
mv %{buildroot}%{_libdir}/libsiftgpu.so %{buildroot}%{_libdir}/libsiftgpu.so.%{version}
ln -s libsiftgpu.so.%{version} %{buildroot}%{_libdir}/libsiftgpu.so

mkdir -p %{buildroot}%{_bindir}
install -m 755 bin/TestWinGlut %{buildroot}%{_bindir}/
install -m 755 bin/SimpleSIFT %{buildroot}%{_bindir}/
install -m 755 bin/speed %{buildroot}%{_bindir}/
install -m 755 bin/MultiThreadSIFT %{buildroot}%{_bindir}/

mkdir -p %{buildroot}%{_docdir}/%{name}.%{version}
install -m 644 doc/manual.pdf %{buildroot}%{_docdir}/%{name}.%{version}

%files
%{_libdir}/libsiftgpu.so.*
%{_bindir}/*
%{_docdir}/%{name}.%{version}/*

%files devel
%{_libdir}/libsiftgpu.so

%changelog
* Thu Oct 30 2014  Attila Zsolt Sajo <sajozsattila@gmail.com>
- Original spec file wroted
