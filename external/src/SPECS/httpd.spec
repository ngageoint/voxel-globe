%include %{_sourcedir}/common.inc

%define mpms worker event
%define contentdir %{_localstatedir}/www
%define suexec_caller apache

Name:		httpd
Version:	2.4.12
Release:	1%{?dist}
Summary:	Apache HTTP Server
Source:		%{name}-%{version}.tar.bz2
Source1:        common.inc
Source2:        httpd.logrotate

License:	ASL 2.0
Group:		System Environment/Daemons
URL: 		http://httpd.apache.org/
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildRequires: autoconf, perl, pkgconfig, findutils
BuildRequires: zlib-devel, libselinux-devel
BuildRequires: apr-devel >= 1.2.0, apr-util-devel >= 1.2.0, pcre-devel >= 5.0
Requires: initscripts >= 8.36, /etc/mime.types, system-logos >= 7.92.1-1	

%description
The Apache HTTP Server is a powerful, efficient, and extensible
web server.

%prep
%setup -q -n %{name}-%{version}

sed -i 's|my $installbuilddir.*|use Cwd "abs_path";\nuse File::Basename;\nmy $prefix2 = abs_path(dirname(__FILE__) . "/%{prefix_bin_rel}");\nmy $installbuilddir = $prefix2 . "/%{httpd_content_prefix_rel}/build/";|' ./support/apxs.in
sed -i -r 's|(^get_config_vars.*)|\1\n$config_vars{"bindir"} = $prefix2."/%{bin_prefix_rel}/";\n$config_vars{"sbindir"} = $prefix2."/%{sbin_prefix_rel}/";\n$config_vars{"libdir"} = $prefix2."/%{lib_prefix_rel}/";\n$config_vars{"sysconfdir"} = $prefix2."/%{sysconf_prefix_rel}/";\n$config_vars{"includedir"} = $prefix2."/%{include_prefix_rel}/";\n$config_vars{"localstatedir"} = $prefix2."/%{localstate_prefix_rel}/";\n$config_vars{"datadir"} = $prefix2."/%{data_prefix_rel}/";\n$config_vars{"exe_prefix"} = $prefix2."/%{exec_prefix_prefix_rel}/";\n|' ./support/apxs.in

%build
#autoheader
#autoconf
autoreconf --force --install

CFLAGS="$RPM_OPT_FLAGS -Wformat-security -fno-strict-aliasing"
SH_LDFLAGS="-Wl,-z,relro"
export CFLAGS SH_LDFLAGS

export ac_cv_path_RSYNC=

function mpmbuild()
{
mpm=$1; shift
mkdir $mpm; pushd $mpm
../configure \
 	--prefix=%{_sysconfdir}/httpd \
 	--exec-prefix=%{_prefix} \
 	--bindir=%{_bindir} \
 	--sbindir=%{_bindir} \
 	--mandir=%{_mandir} \
	--libdir=%{_libdir} \
	--includedir=%{_includedir} \
	--sysconfdir=%{_sysconfdir}/httpd \
	--libexecdir=%{httpd_moddir} \
        --datarootdir=%{_localstatedir}/httpd/ \
        --localstatedir=%{_localstatedir}/httpd/ \
	--datadir=%{contentdir} \
        --with-installbuilddir=%{_libdir}/httpd/build \
	--with-mpm=$mpm \
        --with-apr=%{_roamdir}/apr-1-config --with-apr-util=%{_roamdir}/apu-1-config \
	--enable-suexec --with-suexec \
	--with-suexec-caller=%{suexec_caller} \
	--with-suexec-docroot=%{contentdir} \
	--with-suexec-logfile=%{_localstatedir}/log/httpd/suexec.log \
	--with-suexec-bin=%{_bindir}/suexec \
	--with-suexec-uidmin=500 --with-suexec-gidmin=100 \
        --enable-pie \
        --with-pcre=%{_roamdir}/pcre-config \
        --enable-layout=Apache \
	$*

make %{?_smp_mflags} EXTRA_CFLAGS="-Werror-implicit-function-declaration"
popd
}

# Build everything and the kitchen sink with the prefork build
mpmbuild prefork \
        --enable-mods-shared=all \
	--enable-ssl --with-ssl \
	--enable-proxy \
        --enable-cache \
        --enable-disk-cache \
        --enable-ldap --enable-authnz-ldap \
        --enable-cgid \
        --enable-authn-anon --enable-authn-alias \
        --disable-imagemap \
        --enable-mem-cache \
        --enable-isapi \
        --enable-modules-all

# For the other MPMs, just build httpd and no optional modules
for f in %{mpms}; do
   mpmbuild $f --enable-modules=none
done

#%configure
#%make %{_smp_mflags}

#%check
#LD_LIBRARY_PATH=`pwd`${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
#export LD_LIBRARY_PATH
#make check %{_smp_mflags}

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

pushd prefork
make DESTDIR=$RPM_BUILD_ROOT install
popd

# install alternative MPMs
for f in %{mpms}; do
  install -m 755 ${f}/httpd $RPM_BUILD_ROOT%{_bindir}/httpd.${f}
done

# for holding mod_dav lock database
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/lib/dav

# create a prototype session cache
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/cache/mod_ssl
touch $RPM_BUILD_ROOT%{_localstatedir}/cache/mod_ssl/scache.{dir,pag,sem}

# create cache root
mkdir $RPM_BUILD_ROOT%{_localstatedir}/cache/mod_proxy

# Set up /var directories
#rmdir $RPM_BUILD_ROOT%{_sysconfdir}/httpd/logs
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/log/httpd
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/run/httpd

# install log rotation stuff
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d
install -m 644 -p %{SOURCE2} \
	$RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/httpd

# Make ap_config_layout.h libdir-agnostic
sed -i '/.*DEFAULT_..._LIBEXECDIR/d;/DEFAULT_..._INSTALLBUILDDIR/d' \
    $RPM_BUILD_ROOT%{_includedir}/ap_config_layout.h

# Fix path to instdso in special.mk
sed -i '/instdso/s,top_srcdir,top_builddir,' \
    $RPM_BUILD_ROOT%{contentdir}/build/special.mk

# Make the MMN accessible to module packages
# echo %{mmn} > $RPM_BUILD_ROOT%{_includedir}/httpd/.mmn

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%exclude /usr/lib/debug
%{_bindir}
%{_sysconfdir}
%{_includedir}
%{_libdir}
%{_datadir}
%{_localstatedir}

%post

%postun

#%changelog

