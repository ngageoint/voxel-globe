%include %{_sourcedir}/common.inc

Name:     GeographicLib
Version:	1.42
Release:	1%{?dist}
Summary:	A small set of C++ classes for performing conversions between coordinates
Source:		http://sourceforge.net/projects/geographiclib/files/distrib/GeographicLib-1.42.tar.gz
Source1:  common.inc

Source11: http://sourceforge.net/projects/geographiclib/files/geoids-distrib/egm84-15.tar.bz2
Source12: http://sourceforge.net/projects/geographiclib/files/geoids-distrib/egm84-30.tar.bz2
Source13: http://sourceforge.net/projects/geographiclib/files/geoids-distrib/egm96-5.tar.bz2
Source14: http://sourceforge.net/projects/geographiclib/files/geoids-distrib/egm96-15.tar.bz2
Source15: http://sourceforge.net/projects/geographiclib/files/geoids-distrib/egm2008-1.tar.bz2
Source16: http://sourceforge.net/projects/geographiclib/files/geoids-distrib/egm2008-2_5.tar.bz2
Source17: http://sourceforge.net/projects/geographiclib/files/geoids-distrib/egm2008-5.tar.bz2

Source21: http://sourceforge.net/projects/geographiclib/files/gravity-distrib/grs80.tar.bz2
Source22: http://sourceforge.net/projects/geographiclib/files/gravity-distrib/wgs84.tar.bz2
Source23: http://sourceforge.net/projects/geographiclib/files/gravity-distrib/egm84.tar.bz2
Source24: http://sourceforge.net/projects/geographiclib/files/gravity-distrib/egm96.tar.bz2
Source25: http://sourceforge.net/projects/geographiclib/files/gravity-distrib/egm2008.zip

Source31: http://sourceforge.net/projects/geographiclib/files/magnetic-distrib/igrf11.tar.bz2
Source32: http://sourceforge.net/projects/geographiclib/files/magnetic-distrib/igrf12.tar.bz2
Source33: http://sourceforge.net/projects/geographiclib/files/magnetic-distrib/emm2010.tar.bz2
Source34: http://sourceforge.net/projects/geographiclib/files/magnetic-distrib/wmm2010.tar.bz2
Source35: http://sourceforge.net/projects/geographiclib/files/magnetic-distrib/wmm2015.tar.bz2

License:	MIT/X11
Group:		Development/Library
URL: 		  http://redis.io/
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root

%description
GeographicLib is a small set of C++ classes for performing conversions between
geographic, UTM, UPS, MGRS, geocentric, and local cartesian coordinates, for
gravity (e.g., EGM2008), geoid height and geomagnetic field (e.g., WMM2015)
calculations, and for solving geodesic problems. The emphasis is on returning
accurate results with errors close to round-off (about 5–15 nanometers).
Accurate algorithms for Geodesics on an ellipsoid of revolution and Transverse
Mercator projection have been developed for this library. The functionality of
the library can be accessed from user code, from the Utility programs provided,
or via the Implementations in other languages. Also included is a .NET wrapper
library NETGeographicLib which exposes the functionality to .NET applications.
For a sample of the geodesic capabilities in JavaScript, check out the online
geodesic calculator and the script for displaying geodesics in Google Maps.

This library is not a general purpose projection library; use proj.4 for that.
On the other hand, it does provide the core functionality offered by GEOTRANS.

%package data
Summary:	Development files for GEOS
Group:		Development/Libraries
Requires: 	%{name} = %{version}-%{release}
BuildArch: noarch

%description data
Data files including geoid grid files, gravity and magnetic model.

The geoid heights are computed using interpolation into a rectangular grid. 
The grids are read from data files which have been are computed using the NGA
synthesis programs in the case of the EGM84 and EGM96 models and using the NGA
binary gridded data files in the case of EGM2008. These data files are
available for download: 

GeographicLib can compute the earth's gravitational field with an earth gravity
model using the GravityModel and GravityCircle classes and with the Gravity
utility. These models expand the gravitational potential of the earth as sum
of spherical harmonics. The models also specify a reference ellipsoid, relative
to which geoid heights and gravity disturbances are measured.

GeographicLib can compute the earth's magnetic field by a magnetic model using
the MagneticModel and MagneticCircle classes and with the MagneticField utility.
These models expand the internal magnetic potential of the earth as sum of
spherical harmonics. They neglect magnetic fields due to the ionosphere, the
magnetosphere, nearby magnetized materials, electric machinery, etc. Users of
MagneticModel are advised to read the "Health Warning" this is provided with
igrf11. Although the advice is specific to igrf11, many of the comments apply
to all magnetic field models.

%prep
%setup -q -n %{name}-%{version}

%build
./configure
make %{_smp_mflags}

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
make install prefix="%{buildroot}"
mkdir -p %{buildroot}%{_datadir}/%{name}
pushd %{buildroot}%{_datadir}/%{name}
  tar -jxvf %{SOURCE11}
  tar -jxvf %{SOURCE12}
  tar -jxvf %{SOURCE13}
  tar -jxvf %{SOURCE14}
  tar -jxvf %{SOURCE15}
  tar -jxvf %{SOURCE16}
  tar -jxvf %{SOURCE17}
  tar -jxvf %{SOURCE21}
  tar -jxvf %{SOURCE22}
  tar -jxvf %{SOURCE23}
  tar -jxvf %{SOURCE24}
  unzip %{SOURCE25}
  tar -jxvf %{SOURCE31}
  tar -jxvf %{SOURCE32}
  tar -jxvf %{SOURCE33}
  tar -jxvf %{SOURCE34}
  tar -jxvf %{SOURCE35}
popd

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%exclude %{_datadir}/%{name}
/

%files data
%{_datadir}/%{name}
