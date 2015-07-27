%include %{_sourcedir}/common.inc

Name:		vips
Version:	8.0.2
Release:	1%{?dist}
Summary:	VIPS is a free image processing system
Source:		%{name}-%{version}.tar.gz
Source1:    common.inc

License:	LGPL
Group:		Development/Libraries
URL: 		  http://www.vips.ecs.soton.ac.uk/
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root
BuildRequires:  libgsf >= 1.14.27

%description
VIPS is a free image processing system. It is good with large images (images larger than the amount of RAM you have available), with many CPUs (see Benchmarks for examples of SMP scaling, VIPS is also part of the PARSEC suite), for working with colour, for scientific analysis and for general research & development. As well as JPEG, TIFF and PNG images, it also supports scientific formats like FITS, Matlab, Analyze, PFM, Radiance and OpenSlide. 

%prep
%setup -q -n %{name}-%{version}

%build

%{add_install_flags}
export GSF_LIBS=-lgsf-1
export GSF_CFLAGS="-I%{install_dir}%{_includedir}/libgsf-1"
export FFTW_LIBS="-lfftw3"
export FFTW_CFLAGS=${CFLAGS}
#export OPENSLIDE_LIBS=${LDFLAGS}
#export OPENSLIDE_CFLAGS=${CFLAGS}
%configure
make %{_smp_mflags}

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
%makeinstall

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%exclude /usr/lib/debug
/

