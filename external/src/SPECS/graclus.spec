%include %{_sourcedir}/common.inc

Summary: Graclus is a fast graph clustering software that computes normalized cut and ratio association for a given undirected graph without any eigenvector computation. 
Name: graclus
Version: 1.2
Release: 1%{?dist}
Group: Applications/Multimedia
License: GNU Public License (GPL)
URL: http://www.cs.utexas.edu/users/dml/Software/
Source: graclus1.2.tar.gz
Source1: common.inc
BuildRoot:  %{_builddir}/%{name}-root
Packager: Sajo Zsolt Attila

%description
Graclus (latest: Version 1.2) is a fast graph clustering software that computes normalized cut and ratio association for a given undirected graph without any eigenvector computation. This is possible because of the mathematical equivalence between general cut or association objectives (including normalized cut and ratio association) and the weighted kernel k-means objective. One important implication of this equivalence is that we can run a k-means type of iterative algorithm to minimize general cut or association objectives. Therefore unlike spectral methods, our algorithm totally avoids time-consuming eigenvector computation. We have embedded the weighted kernel k-means algorithm in a multilevel framework to develop very fast software for graph clustering. 

%prep
%setup -n %{name}%{version}

%build
make COPTIONS=-DNUMBITS=64

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

rm -rf %{buildroot}
mkdir -p %{buildroot}%{_bindir}/
install -m 755 graclus %{buildroot}%{_bindir}/

mkdir -p %{buildroot}%{_libdir}
install -m 644 libmultilevel.a %{buildroot}%{_libdir}
install -m 644 libmetis.a %{buildroot}%{_libdir}
mkdir -p %{buildroot}%{_includedir}/metisLib
install -m 644 metisLib/*.h %{buildroot}%{_includedir}/metisLib

%files
%{_bindir}/graclus
%{_libdir}/libmultilevel.a
%{_libdir}/libmetis.a
%{_includedir}/metisLib/macros.h
%{_includedir}/metisLib/struct.h
%{_includedir}/metisLib/rename.h
%{_includedir}/metisLib/proto.h
%{_includedir}/metisLib/defs.h
%{_includedir}/metisLib/metis.h

%changelog
* Thu Oct 30 2014  Attila Zsolt Sajo <sajozsattila@gmail.com>
- Original spec file wroted