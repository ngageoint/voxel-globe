%include %{_sourcedir}/common.inc
Source999:        common.inc
%global real_name gcc
Name: %{real_name}%{name_suffix}
Provides: %{real_name}%{provides_suffix}

License:      GPLv2
Group:        Development/Languages/Other
Summary:      Various compilers (C, C++, Objective-C, Java, ...)
Version:      4.9.3
Release:      1%{?dist}
URL:          https://gcc.gnu.org/
BuildRoot:    %{_tmppath}/%{name}-%{version}-build
Source0:      ftp://ftp.gnu.org/gnu/%{real_name}/%{real_name}-%{version}/%{real_name}-%{version}.tar.bz2
BuildRequires: libmpc-devel >= 0.8.0
BuildRequires: mpfr-devel >= 2.4.0
BuildRequires: gmp-devel >= 4.2

%description
The gcc package contains the GNU Compiler Collection version 4.
You'll need this package in order to compile C code.

%prep
%setup -q -n %{real_name}-%{version}

%build
echo %(echo ${VIP_INSTALL_DIR})
%{_configure} --disable-multilib --enable-languages=c,c++ \
              --enable-linker-build-id \
              --prefix=%{_prefix}\
              --exec-prefix=%{_exec_prefix} \
              --bindir=%{_bindir} \
              --sbindir=%{_sbindir} \
              --libexecdir=%{_libexecdir} \
              --sysconfdir=%{_sysconfdir} \
              --sharedstatedir=%{_sharedstatedir} \
              --localstatedir=%{_localstatedir} \
              --libdir=%{_libdir} \
              --includedir=%{_includedir} \
              --oldincludedir=%{_includedir} \
              --datarootdir=%{_datarootdir} \
              --datadir=%{_datadir} \
              --infodir=%{_infodir} \
              --localedir=%{_localedir} \
              --mandir=%{_mandir} \
              --docdir=%{_docdir} \
              --with-gmp=%{install_dir} \
              --with-mpfr=%{install_dir}

make %{?_smp_mflags} DESTDIR="%{buildroot}"

%install

%{__make} install DESTDIR="%{buildroot}"
mv %{buildroot}/lib64/* %{buildroot}%{_libdir}/
rm %{buildroot}%{_infodir}/dir

%files
%{_bindir}/*
%{_includedir}/c++/%{version}
%{_libdir}/*.*
%{_libdir}/%{real_name}/x86_64-unknown-linux-gnu/%{version}
%{_libexecdir}/%{real_name}/x86_64-unknown-linux-gnu/%{version}
%{_datadir}/%{real_name}-%{version}
%{_infodir}/*
%{_datadir}/locale/*
%{_mandir}/man1/*
%{_mandir}/man7/*