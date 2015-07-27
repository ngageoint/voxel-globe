%include %{_sourcedir}/common.inc

Summary: Implementation of new inexact Newton type Bundle Adjustment algorithms that exploit hardware parallelism for efficiently solving large scale 3D scene reconstruction problems.
Name: pba
Version: 1.0.5
Release: 1%{?dist}
Group: Applications/Multimedia
License: GNU Public License (GPL)
URL: http://grail.cs.washington.edu/projects/mcba/
Source: pba_v1.0.5.zip
Source1: common.inc
BuildRoot:  %{_builddir}/%{name}-root
Packager: Sajo Zsolt Attila

%package        devel
Summary:	Development files for PBA
Group:		Development/Libraries
Requires: 	%{name} = %{version}-%{release}


%description
The emergence of multi-core computers represents a fundamental shift, with major implications for the design of computer vision algorithms. Most computers sold today have a multicore CPU with 2-16 cores and a GPU with anywhere from 4 to 128 cores. Exploiting this hardware parallelism will be key to the success and scalability of computer vision algorithms in the future. In this project, we consider the design and implementation of new inexact Newton type Bundle Adjustment algorithms that exploit hardware parallelism for efficiently solving large scale 3D scene reconstruction problems. We explore the use of multicore CPU as well as multicore GPUs for this purpose. We show that overcoming the severe memory and bandwidth limitations of current generation GPUs not only leads to more space efficient algorithms, but also to surprising savings in runtime. Our CPU based system is up to ten times and our GPU based system is up to thirty times faster than the current state of the art methods, while maintaining comparable convergence behavior.

%description devel
The %{name}-devel package contains development files for %{name}.

%prep
%setup -n pba

%build
%if 0%{?ubuntu} || 0%{?mint}
export CUDA_BIN_PATH=/usr/bin
export CUDA_LIB_PATH=/usr/lib/x86_64-linux-gnu
%endif
#Allow this to fail
make -f makefile ;:

make -f makefile_no_gpu

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

mkdir -p %{buildroot}%{_libdir}/
mkdir -p %{buildroot}%{_includedir}/pba

install -m 644 bin/libpba*.so %{buildroot}%{_libdir}/
install -m 644 bin/libpba*.a %{buildroot}%{_libdir}/

install -m 644 src/pba/pba.h %{buildroot}%{_includedir}/pba/
install -m 644 src/pba/DataInterface.h %{buildroot}%{_includedir}/pba/
install -m 644 src/pba/ConfigBA.h %{buildroot}%{_includedir}/pba/

%files
%{_libdir}/libpba*.so

%files devel
%{_libdir}/libpba*.a
%dir %{_includedir}/pba
%{_includedir}/pba/*.h

%changelog
* Thu Oct 30 2014  Attila Zsolt Sajo <sajozsattila@gmail.com>
- Original spec file wroted
