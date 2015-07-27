%include %{_sourcedir}/common.inc

%define beta 0

# This is a macro to be used with find_lang and other stuff
%define majorversion 9.4
%define packageversion 94
%define oname postgresql

%{!?test:%define test 1}
%{!?plpython:%define plpython 1}
%{!?pltcl:%define pltcl 1}
%{!?plperl:%define plperl 1}
%{!?ssl:%define ssl 1}
%{!?intdatetimes:%define intdatetimes 1}
%{!?kerberos:%define kerberos 1}
%{!?nls:%define nls 0} 
#I have NO IDEA how to get nls working
%{!?xml:%define xml 1}
%{!?pam:%define pam 1}
%{!?disablepgfts:%define disablepgfts 0}
%{!?runselftest:%define runselftest 0 }
%{!?uuid:%define uuid 1}
%{!?ldap:%define ldap 1}

Name:		postgresql
Version:	9.4.2
Release:	1%{?dist}
Summary:	PostgreSQL client programs and libraries
Source:		%{name}-%{version}.tar.bz2
Source1:        common.inc
Source4:	postgresql_Makefile.regress
Source5:	pg_config.h
Source7:	ecpg_config.h
Source14:	postgresql.pam

License:	PostgreSQL
Group:		Applications/Databases
URL: 		http://www.postgresql.org/
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root
BuildRequires:	perl glibc-devel bison flex

%if %plperl
BuildRequires: perl-ExtUtils-Embed
BuildRequires: perl(ExtUtils::MakeMaker) 
%endif

%if %plpython
BuildRequires:	python-devel
%endif

%if %pltcl
BuildRequires:	tcl-devel
%endif

BuildRequires:	readline-devel
BuildRequires:	zlib-devel >= 1.0.4

%if %ssl
BuildRequires:	openssl-devel
%endif

%if %kerberos
BuildRequires:	krb5-devel
BuildRequires:	e2fsprogs-devel
%endif

%if %nls
BuildRequires:	gettext >= 0.10.35
%endif

%if %xml
BuildRequires:	libxml2-devel libxslt-devel
%endif

%if %pam
BuildRequires:	pam-devel
%endif

%if %uuid
BuildRequires:	uuid-devel
%endif

%if %ldap
BuildRequires:	openldap-devel
%endif

Requires:	%{name}-libs = %{version}-%{release}
Provides:	postgresql

%description
PostgreSQL is an advanced Object-Relational database management system
(DBMS) that supports almost all SQL constructs (including
transactions, subselects and user-defined types and functions). The
postgresql package includes the client programs and libraries that
you'll need to access a PostgreSQL DBMS server.  These PostgreSQL
client programs are programs that directly manipulate the internal
structure of PostgreSQL databases on a PostgreSQL server. These client
programs can be located on the same machine with the PostgreSQL
server, or may be on a remote machine which accesses a PostgreSQL
server over a network connection. This package contains the command-line 
utilities for managing PostgreSQL databases on a PostgreSQL server. 

If you want to manipulate a PostgreSQL database on a local or remote PostgreSQL
server, you need this package. You also need to install this package
if you're installing the postgresql93-server package.

%package libs
Summary:	The shared libraries required for any PostgreSQL clients
Group:		Applications/Databases
Provides:	libpq.so
Provides:	postgresql-libs

%description libs
The postgresql93-libs package provides the essential shared libraries for any 
PostgreSQL client program or interface. You will need to install this package
to use any other PostgreSQL package or any clients that need to connect to a
PostgreSQL server.

%package server
Summary:	The programs needed to create and run a PostgreSQL server
Group:		Applications/Databases
Requires:	/usr/sbin/useradd /sbin/chkconfig 
Requires:	%{name} = %{version}-%{release}
Provides:	postgresql-server

%description server
The postgresql93-server package includes the programs needed to create
and run a PostgreSQL server, which will in turn allow you to create
and maintain PostgreSQL databases.  PostgreSQL is an advanced
Object-Relational database management system (DBMS) that supports
almost all SQL constructs (including transactions, subselects and
user-defined types and functions). You should install
postgresql93-server if you want to create and maintain your own
PostgreSQL databases and/or your own PostgreSQL server. You also need
to install the postgresql package.

%package docs
Summary:	Extra documentation for PostgreSQL
Group:		Applications/Databases
Provides:	postgresql-docs

%description docs
The postgresql93-docs package includes the SGML source for the documentation
as well as the documentation in PDF format and some extra documentation.
Install this package if you want to help with the PostgreSQL documentation
project, or if you want to generate printed documentation. This package also 
includes HTML version of the documentation.

%package contrib
Summary:	Contributed source and binaries distributed with PostgreSQL
Group:		Applications/Databases
Requires:	%{name} = %{version}
Provides:	postgresql-contrib

%description contrib
The postgresql93-contrib package contains contributed packages that are
included in the PostgreSQL distribution.

%package devel
Summary:	PostgreSQL development header files and libraries
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}
Provides:	postgresql-devel

%description devel
The postgresql93-devel package contains the header files and libraries
needed to compile C or C++ applications which will directly interact
with a PostgreSQL database management server and the ecpg Embedded C
Postgres preprocessor. You need to install this package if you want to
develop applications which will interact with a PostgreSQL server. 

%if %plperl
%package plperl
Summary:	The Perl procedural language for PostgreSQL
Group:		Applications/Databases
Requires:	%{name}-server = %{version}-%{release}
%ifarch ppc ppc64
BuildRequires:	perl-devel
%endif
Obsoletes:	postgresql-pl
Provides:	postgresql-plperl

%description plperl
PostgreSQL is an advanced Object-Relational database management
system. The postgresql93-plperl package contains the PL/Perl language
for the backend.
%endif

%if %plpython
%package plpython
Summary:	The Python procedural language for PostgreSQL
Group:		Applications/Databases
Requires:	%{name} = %{version}
Requires:	%{name}-server = %{version}
Obsoletes:	postgresql-pl
Provides:	postgresql-plpython

%description plpython
PostgreSQL is an advanced Object-Relational database management
system. The postgresql93-plpython package contains the PL/Python language
for the backend.
%endif

%if %pltcl
%package pltcl
Summary:	The Tcl procedural language for PostgreSQL
Group:		Applications/Databases
Requires:	%{name} = %{version}
Requires:	%{name}-server = %{version}
Obsoletes:	postgresql-pl
Provides:	postgresql-pltcl

%description pltcl
PostgreSQL is an advanced Object-Relational database management
system. The postgresql93-pltcl package contains the PL/Tcl language
for the backend.
%endif

%if %test
%package test
Summary:	The test suite distributed with PostgreSQL
Group:		Applications/Databases
Requires:	%{name}-server = %{version}-%{release}
Provides:	postgresql-test

%description test
PostgreSQL is an advanced Object-Relational database management
system. The postgresql-test package includes the sources and pre-built
binaries of various tests for the PostgreSQL database management
system, including regression tests and benchmarks.
%endif

%prep
%setup -q -n %{name}-%{version}
#sed -i 's|override \w*dir.*||' ./src/Makefile.global.in

%build

CFLAGS="${CFLAGS:-%optflags}" ; export CFLAGS
CXXFLAGS="${CXXFLAGS:-%optflags}" ; export CXXFLAGS
%if %kerberos
CPPFLAGS="${CPPFLAGS} -I%{_includedir}/et" ; export CPPFLAGS
CFLAGS="${CFLAGS} -I%{_includedir}/et" ; export CFLAGS
%endif

# Strip out -ffast-math from CFLAGS....

CFLAGS=`echo $CFLAGS|xargs -n 1|grep -v ffast-math|xargs -n 100`

export LIBNAME=%{_lib}
export PYTHON=%{__python}

%{add_install_flags}

./configure \
	--prefix=%{_prefix} \
	--includedir=%{re_prefix}%{_includedir} \
	--mandir=%{re_prefix}%{_mandir} \
	--datarootdir=%{re_prefix}%{_datadir} \
        --sysconfdir=%{re_prefix}%{_sysconfdir} \
        --libdir=%{re_prefix}%{_libdir} \
%if %beta
	--enable-debug \
	--enable-cassert \
%endif
%if %plperl
	--with-perl \
%endif
%if %plpython
	--with-python \
%endif
%if %pltcl
	--with-tcl \
%endif #	--with-tclconfig=%{tclconfig_dir} \
%if %ssl
	--with-openssl \
%endif
%if %pam
	--with-pam \
%endif
%if %kerberos
	--with-krb5 \
	--with-gssapi \
	--with-includes=%{kerbdir}/include \
	--with-libraries=%{kerbdir}/%{_lib} \
%endif
%if %nls
	--enable-nls \
%endif
%if !%intdatetimes
	--disable-integer-datetimes \
%endif
%if %disablepgfts
	--disable-thread-safety \
%endif
%if %uuid
	--with-ossp-uuid \
%endif
%if %xml
	--with-libxml \
	--with-libxslt \
%endif
%if %ldap
	--with-ldap \
%endif
        --disable-rpath
#	--with-system-tzdata=%{re_prefix}%{_datadir}/zoneinfo
#Breaks portability because postgres needs to be patched to fix this

make %{?_smp_mflags} all
make %{?_smp_mflags} -C contrib all
%if %uuid
make %{?_smp_mflags} -C contrib/uuid-ossp all
%endif

# Have to hack makefile to put correct path into tutorial scripts
sed "s|C=\`pwd\`;|C=%{_libdir}/tutorial;|" < src/tutorial/Makefile > src/tutorial/GNUmakefile
make %{?_smp_mflags} -C src/tutorial NO_PGXS=1 all
rm -f src/tutorial/GNUmakefile

%if %runselftest
	pushd src/test/regress
env DISPLAY=:0.0 xterm
	make all
	cp ../../../contrib/spi/refint.so .
	cp ../../../contrib/spi/autoinc.so .
	make MAX_CONNECTIONS=5 check
	make clean
	popd
	pushd src/pl
	make MAX_CONNECTIONS=5 check
	popd
	pushd contrib
	make MAX_CONNECTIONS=5 check
	popd
%endif

%if %test
	pushd src/test/regress
	make all
	popd
%endif


%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

make DESTDIR=%{buildroot} install
mkdir -p %{buildroot}%{_datadir}/extensions/
make -C contrib DESTDIR=%{buildroot} install
%if %uuid
make -C contrib/uuid-ossp DESTDIR=%{buildroot} install
%endif

# multilib header hack; note pg_config.h is installed in two places!
# we only apply this to known Red Hat multilib arches, per bug #177564
case `uname -i` in
	i386 | x86_64 | ppc | ppc64 | s390 | s390x)
		mv %{buildroot}%{_includedir}/pg_config.h %{buildroot}%{_includedir}/pg_config_`uname -i`.h
		install -m 644 %{SOURCE5} %{buildroot}%{_includedir}/
#		mv %{buildroot}%{_includedir}/server/pg_config.h %{buildroot}%{_includedir}/server/pg_config_`uname -i`.h
#		install -m 644 %{SOURCE5} %{buildroot}%{_includedir}/server/
		mv %{buildroot}%{_includedir}/ecpg_config.h %{buildroot}%{_includedir}/ecpg_config_`uname -i`.h
		install -m 644 %{SOURCE7} %{buildroot}%{_includedir}/
		;;
	*)
	;;
esac

#install -d %{buildroot}/etc/rc.d/init.d
#sed 's/^PGVERSION=.*$/PGVERSION=%{version}/' <%{SOURCE3} > postgresql.init
#install -m 755 postgresql.init %{buildroot}/etc/rc.d/init.d/postgresql-%{majorversion}

%if %pam
install -d %{buildroot}%{_sysconfdir}/pam.d
install -m 644 %{SOURCE14} %{buildroot}%{_sysconfdir}/pam.d/postgresql%{packageversion}
%endif

# PGDATA needs removal of group and world permissions due to pg_pwd hole.
# install -d -m 700 %{buildroot}/var/lib/pgsql/%{majorversion}/data

# backups of data go here...
# install -d -m 700 %{buildroot}/var/lib/pgsql/%{majorversion}/backups

# Create the multiple postmaster startup directory
# install -d -m 700 %{buildroot}/etc/sysconfig/pgsql/%{majorversion}

# Install linker conf file under postgresql installation directory.
# We will install the latest version via alternatives.
#install -d -m 755 %{buildroot}%{_datadir}/
#install -m 700 %{SOURCE9} %{buildroot}%{_datadir}/

%if %test
	# tests. There are many files included here that are unnecessary,
	# but include them anyway for completeness.  We replace the original
	# Makefiles, however.
	mkdir -p %{buildroot}%{_libdir}/test
	cp -a src/test/regress %{buildroot}%{_libdir}/test
	install -m 0755 contrib/spi/refint.so %{buildroot}%{_libdir}/test/regress
	install -m 0755 contrib/spi/autoinc.so %{buildroot}%{_libdir}/test/regress
	pushd  %{buildroot}%{_libdir}/test/regress
	strip *.so
	rm -f GNUmakefile Makefile *.o
	chmod 0755 pg_regress regress.so
	popd
	cp %{SOURCE4} %{buildroot}%{_libdir}/test/regress/Makefile
	chmod 0644 %{buildroot}%{_libdir}/test/regress/Makefile
%endif

# Fix some more documentation
# gzip doc/internals.ps
#cp %{SOURCE6} README.rpm-dist
mkdir -p %{buildroot}%{_docdir}/html
mv doc/src/sgml/html doc
mkdir -p %{buildroot}%{_mandir}/
mv doc/src/sgml/man1 doc/src/sgml/man3 doc/src/sgml/man7  %{buildroot}%{_mandir}/
rm -rf %{buildroot}%{_docdir}/pgsql

# initialize file lists
cp /dev/null main.lst
cp /dev/null libs.lst
cp /dev/null server.lst
cp /dev/null devel.lst
cp /dev/null plperl.lst
cp /dev/null pltcl.lst
cp /dev/null plpython.lst
touch pg_main.lst
touch pg_libpq5.lst
touch pg_server.lst
touch pg_devel.lst
touch pg_plperl.lst
touch pg_plpython.lst
touch pg_pltcl.lst


%if %nls
%find_lang ecpg
%find_lang ecpglib6
%find_lang initdb
%find_lang libpq5
%find_lang pg_basebackup
%find_lang pg_config
%find_lang pg_controldata
%find_lang pg_ctl
%find_lang pg_dump
%find_lang pg_resetxlog
%find_lang pgscripts
%if %plperl
%find_lang plperl
cat plperl.lang > pg_plperl.lst
%endif
%find_lang plpgsql
%if %plpython
%find_lang plpython
cat plpython.lang > pg_plpython.lst
%endif
%if %pltcl
%find_lang pltcl
cat pltcl.lang > pg_pltcl.lst
%endif
%find_lang postgres
%find_lang psql

cat libpq5.lang > pg_libpq5.lst
cat pg_config.lang ecpg.lang ecpglib6.lang > pg_devel.lst
cat initdb.lang pg_ctl.lang psql.lang pg_dump.lang pg_basebackup.lang pgscripts.lang > pg_main.lst
cat postgres.lang pg_resetxlog.lang pg_controldata.lang plpgsql.lang > pg_server.lst

%endif

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files -f pg_main.lst
%defattr(-,root,root)
%doc doc/KNOWN_BUGS doc/MISSING_FEATURES 
%doc COPYRIGHT doc/bug.template
#%doc README.rpm-dist
%{_bindir}/clusterdb
%{_bindir}/createdb
%{_bindir}/createlang
%{_bindir}/createuser
%{_bindir}/dropdb
%{_bindir}/droplang
%{_bindir}/dropuser
%{_bindir}/pg_basebackup
%{_bindir}/pg_config
%{_bindir}/pg_dump
%{_bindir}/pg_dumpall
%{_bindir}/pg_isready
%{_bindir}/pg_restore
%{_bindir}/pg_recvlogical
%{_bindir}/pg_test_fsync
%{_bindir}/pg_receivexlog
%{_bindir}/psql
%{_bindir}/reindexdb
%{_bindir}/vacuumdb
%{_mandir}/man1/clusterdb.*
%{_mandir}/man1/createdb.*
%{_mandir}/man1/createlang.*
%{_mandir}/man1/createuser.*
%{_mandir}/man1/dropdb.*
%{_mandir}/man1/droplang.*
%{_mandir}/man1/dropuser.*
%{_mandir}/man1/pg_basebackup.*
%{_mandir}/man1/pg_config.*
%{_mandir}/man1/pg_dump.*
%{_mandir}/man1/pg_dumpall.*
%{_mandir}/man1/pg_isready.*
%{_mandir}/man1/pg_receivexlog.*
%{_mandir}/man1/pg_recvlogical.*
%{_mandir}/man1/pg_restore.*
%{_mandir}/man1/psql.*
%{_mandir}/man1/reindexdb.*
%{_mandir}/man1/vacuumdb.*
%{_mandir}/man3/*
%{_mandir}/man7/*

%files docs
%defattr(-,root,root)
%doc doc/src/*
#%doc *-A4.pdf
%doc src/tutorial
%doc doc/html
%{_docdir}/%{oname}/extension/*.example

%files contrib
%defattr(-,root,root)
%{_libdir}/%{oname}/_int.so
%{_libdir}/%{oname}/adminpack.so
%{_libdir}/%{oname}/auth_delay.so
%{_libdir}/%{oname}/autoinc.so
%{_libdir}/%{oname}/auto_explain.so
%{_libdir}/%{oname}/btree_gin.so
%{_libdir}/%{oname}/btree_gist.so
%{_libdir}/%{oname}/chkpass.so
%{_libdir}/%{oname}/citext.so
%{_libdir}/%{oname}/cube.so
%{_libdir}/%{oname}/dblink.so
%{_libdir}/%{oname}/dummy_seclabel.so
%{_libdir}/%{oname}/earthdistance.so
%{_libdir}/%{oname}/file_fdw.so*
%{_libdir}/%{oname}/fuzzystrmatch.so
%{_libdir}/%{oname}/insert_username.so
%{_libdir}/%{oname}/isn.so
%{_libdir}/%{oname}/hstore.so
%{_libdir}/%{oname}/passwordcheck.so
%{_libdir}/%{oname}/pg_freespacemap.so
%{_libdir}/%{oname}/pg_stat_statements.so
%{_libdir}/%{oname}/pgrowlocks.so
%{_libdir}/%{oname}/postgres_fdw.so
%{_libdir}/%{oname}/sslinfo.so
%{_libdir}/%{oname}/lo.so
%{_libdir}/%{oname}/ltree.so
%{_libdir}/%{oname}/moddatetime.so
%{_libdir}/%{oname}/pageinspect.so
%{_libdir}/%{oname}/pgcrypto.so
%{_libdir}/%{oname}/pgstattuple.so
%{_libdir}/%{oname}/pg_buffercache.so
%{_libdir}/%{oname}/pg_trgm.so
%{_libdir}/%{oname}/pg_upgrade_support.so
%{_libdir}/%{oname}/refint.so
%{_libdir}/%{oname}/seg.so
%{_libdir}/%{oname}/tablefunc.so
%{_libdir}/%{oname}/tcn.so
%{_libdir}/%{oname}/timetravel.so
%{_libdir}/%{oname}/unaccent.so
%{_libdir}/%{oname}/worker_spi.so
%{_libdir}/%{oname}/pg_prewarm.so
%{_libdir}/%{oname}/test_decoding.so
%{_libdir}/%{oname}/test_shm_mq.so
%if %xml
%{_libdir}/%{oname}/pgxml.so
%endif
%if %uuid
%{_libdir}/%{oname}/uuid-ossp.so
%endif
%{_datadir}/%{oname}/extension/adminpack*
%{_datadir}/%{oname}/extension/autoinc*
%{_datadir}/%{oname}/extension/btree_gin*
%{_datadir}/%{oname}/extension/btree_gist*
%{_datadir}/%{oname}/extension/chkpass*
%{_datadir}/%{oname}/extension/citext*
%{_datadir}/%{oname}/extension/cube*
%{_datadir}/%{oname}/extension/dblink*
%{_datadir}/%{oname}/extension/dict_int*
%{_datadir}/%{oname}/extension/dict_xsyn*
%{_datadir}/%{oname}/extension/earthdistance*
%{_datadir}/%{oname}/extension/file_fdw*
%{_datadir}/%{oname}/extension/fuzzystrmatch*
%{_datadir}/%{oname}/extension/hstore*
%{_datadir}/%{oname}/extension/insert_username*
%{_datadir}/%{oname}/extension/intagg*
%{_datadir}/%{oname}/extension/intarray*
%{_datadir}/%{oname}/extension/isn*
%{_datadir}/%{oname}/extension/lo*
%{_datadir}/%{oname}/extension/ltree*
%{_datadir}/%{oname}/extension/moddatetime*
%{_datadir}/%{oname}/extension/pageinspect*
%{_datadir}/%{oname}/extension/pg_buffercache*
%{_datadir}/%{oname}/extension/pg_freespacemap*
%{_datadir}/%{oname}/extension/pg_prewarm*
%{_datadir}/%{oname}/extension/pg_stat_statements*
%{_datadir}/%{oname}/extension/pg_trgm*
%{_datadir}/%{oname}/extension/pgcrypto*
%{_datadir}/%{oname}/extension/pgrowlocks*
%{_datadir}/%{oname}/extension/pgstattuple*
%{_datadir}/%{oname}/extension/postgres_fdw*
%{_datadir}/%{oname}/extension/refint*
%{_datadir}/%{oname}/extension/seg*
%{_datadir}/%{oname}/extension/sslinfo*
%{_datadir}/%{oname}/extension/tablefunc*
%{_datadir}/%{oname}/extension/tcn*
%{_datadir}/%{oname}/extension/test_parser*
%{_datadir}/%{oname}/extension/test_shm_mq*
%{_datadir}/%{oname}/extension/timetravel*
%{_datadir}/%{oname}/extension/tsearch2*
%{_datadir}/%{oname}/extension/unaccent*
%if %uuid
%{_datadir}/%{oname}/extension/uuid-ossp*
%endif
%{_datadir}/%{oname}/extension/worker_spi*
%{_datadir}/%{oname}/extension/xml2*
%{_bindir}/oid2name
%{_bindir}/pgbench
%{_bindir}/vacuumlo
%{_bindir}/pg_archivecleanup
%{_bindir}/pg_standby
%{_bindir}/pg_test_timing
%{_bindir}/pg_upgrade
%{_bindir}/pg_xlogdump
%{_mandir}/man1/oid2name.1
%{_mandir}/man1/pg_archivecleanup.1
%{_mandir}/man1/pg_standby.1
%{_mandir}/man1/pg_test_fsync.1
%{_mandir}/man1/pg_test_timing.1
%{_mandir}/man1/pg_upgrade.1
%{_mandir}/man1/pg_xlogdump.1
%{_mandir}/man1/pgbench.1
%{_mandir}/man1/vacuumlo.1



%files libs -f pg_libpq5.lst
%defattr(-,root,root)
%{_libdir}/libpq.so.*
%{_libdir}/libecpg.so*
%{_libdir}/libpgtypes.so.*
%{_libdir}/libecpg_compat.so.*
%{_libdir}/%{oname}/libpqwalreceiver.so
#%config(noreplace) %{_datadir}/postgresql-9.3-libs.conf

%files server -f pg_server.lst
%defattr(-,root,root)
#%config(noreplace) /etc/rc.d/init.d/postgresql-%{majorversion}
#%if %pam
#%config(noreplace) /etc/pam.d/postgresql%{packageversion}
%config(noreplace) %{_sysconfdir}/pam.d/postgresql%{packageversion}
#%endif
#%attr (755,root,root) %dir /etc/sysconfig/pgsql
%{_bindir}/initdb
%{_bindir}/pg_controldata
%{_bindir}/pg_ctl
%{_bindir}/pg_resetxlog
%{_bindir}/postgres
%{_bindir}/postmaster
%{_mandir}/man1/initdb.*
%{_mandir}/man1/pg_controldata.*
%{_mandir}/man1/pg_ctl.*
%{_mandir}/man1/pg_resetxlog.*
%{_mandir}/man1/postgres.*
%{_mandir}/man1/postmaster.*
%{_datadir}/%{oname}/postgres.bki
%{_datadir}/%{oname}/postgres.description
%{_datadir}/%{oname}/postgres.shdescription
%{_datadir}/%{oname}/system_views.sql
%{_datadir}/%{oname}/*.sample
%{_datadir}/%{oname}/timezone/*
%{_datadir}/%{oname}/timezonesets/*
%{_datadir}/%{oname}/tsearch_data/*.affix
%{_datadir}/%{oname}/tsearch_data/*.dict
%{_datadir}/%{oname}/tsearch_data/*.ths
%{_datadir}/%{oname}/tsearch_data/*.rules
%{_datadir}/%{oname}/tsearch_data/*.stop
%{_datadir}/%{oname}/tsearch_data/*.syn
%{_libdir}/%{oname}/dict_int.so
%{_libdir}/%{oname}/dict_snowball.so
%{_libdir}/%{oname}/dict_xsyn.so
%{_libdir}/%{oname}/euc2004_sjis2004.so
%{_libdir}/%{oname}/plpgsql.so
%dir %{_datadir}/%{oname}/extension
%{_datadir}/%{oname}/extension/plpgsql*
%{_libdir}/%{oname}/test_parser.so
%{_libdir}/%{oname}/tsearch2.so

%dir %{_libdir}
%dir %{_datadir}/%{oname}
#%attr(700,postgres,postgres) %dir /var/lib/pgsql
#%attr(700,postgres,postgres) %dir /var/lib/pgsql/%{majorversion}
#%attr(700,postgres,postgres) %dir /var/lib/pgsql/%{majorversion}/data
#%attr(700,postgres,postgres) %dir /var/lib/pgsql/%{majorversion}/backups
%{_libdir}/%{oname}/*_and_*.so
%{_datadir}/%{oname}/conversion_create.sql
%{_datadir}/%{oname}/information_schema.sql
%{_datadir}/%{oname}/snowball_create.sql
%{_datadir}/%{oname}/sql_features.txt

%files devel -f pg_devel.lst
%defattr(-,root,root)
%{_includedir}/*
%{_bindir}/ecpg
%{_libdir}/libpq.so
%{_libdir}/libecpg.so
%{_libdir}/libpq.a
%{_libdir}/libpgcommon.a
%{_libdir}/libecpg.a
%{_libdir}/libecpg_compat.so
%{_libdir}/libecpg_compat.a
%{_libdir}/libpgport.a
%{_libdir}/libpgtypes.so
%{_libdir}/libpgtypes.a
%{_libdir}/%{oname}/pgxs/*
%{_libdir}/pkgconfig/*
%{_mandir}/man1/ecpg.*

%if %plperl
%files plperl -f pg_plperl.lst
%defattr(-,root,root)
%{_libdir}/%{oname}/plperl.so
%{_datadir}/%{oname}/extension/plperl*
%endif

%if %pltcl
%files pltcl -f pg_pltcl.lst
%defattr(-,root,root)
%{_libdir}/%{oname}/pltcl.so
%{_bindir}/pltcl_delmod
%{_bindir}/pltcl_listmod
%{_bindir}/pltcl_loadmod
%{_datadir}/%{oname}/unknown.pltcl
%{_datadir}/%{oname}/extension/pltcl*
%endif

%if %plpython
%files plpython -f pg_plpython.lst
%defattr(-,root,root)
%{_libdir}/%{oname}/plpython*.so
%{_datadir}/%{oname}/extension/plpython2u*
%{_datadir}/%{oname}/extension/plpythonu*
%endif

%if %test
%files test
%defattr(-,postgres,postgres)
%attr(-,postgres,postgres) %{_libdir}/test/*
%attr(-,postgres,postgres) %dir %{_libdir}/test
%endif

%changelog
* Tue Mar 18 2014 Devrim GÜNDÜZ <devrim@gunduz.org> - 9.3.4-1PGDG
- Update to 9.3.4, per changes described at:
  http://www.postgresql.org/docs/9.3/static/release-9-3-4.html

* Tue Feb 18 2014 Devrim GÜNDÜZ <devrim@gunduz.org> - 9.3.3-1PGDG
- Update to 9.3.3, per changes described at:
  http://www.postgresql.org/docs/9.3/static/release-9-3-3.html

* Thu Dec 12 2013 Devrim GÜNDÜZ <devrim@gunduz.org> - 9.3.2-2PGDG
- Fix builds when uuid support is disabled, by adding missing conditional.
- Add process name to the status() call in init script.
  Patch from Darrin Smart

* Wed Dec 04 2013 Devrim GÜNDÜZ <devrim@gunduz.org> - 9.3.2-1PGDG
- Update to 9.3.2, per changes described at:
  http://www.postgresql.org/docs/9.3/static/release-9-3-2.html

* Tue Oct 8 2013 Devrim GÜNDÜZ <devrim@gunduz.org> - 9.3.1-1PGDG
- Update to 9.3.1, per changes described at:
  http://www.postgresql.org/docs/9.3/static/release-9-3-1.html
- Fix issues with init script, per http://wiki.pgrpms.org/ticket/136.

* Tue Sep 3 2013 Devrim GÜNDÜZ <devrim@gunduz.org> - 9.3.0-1PGDG
- Update to 9.3.0

* Tue Aug 20 2013 Devrim GÜNDÜZ <devrim@gunduz.org> - 9.3rc1-1PGDG
- Update to 9.3 RC1

* Wed Jun 26 2013 Jeff Frost <jeff@pgexperts.com> - 9.3beta2-1PGDG
- Update to 9.3 beta 2

* Tue May 14 2013 Devrim GÜNDÜZ <devrim@gunduz.org> - 9.3beta1-4PGDG
- Revert #90. Per a report in pgsql-bugs mailing list.

* Mon May 13 2013 Devrim GÜNDÜZ <devrim@gunduz.org> - 9.3beta1-3PGDG
- Fix paths in init script. Per repor from Vibhor Kumar.

* Sun May 12 2013 Devrim GÜNDÜZ <devrim@gunduz.org> - 9.3beta1-2PGDG
- Support separated xlog directory at initdb. Per suggestion from
  Magnus Hagander. Fixes #90.
- Remove hardcoded script names in init script. Fixes #102.
- Add support for pg_ctl promote. Per suggestion from Magnus Hagander.
  Fixes #93.
- Set log_line_prefix in default config file to %m. Per suggestion
  from Magnus. Fixes #91.

* Tue May 07 2013 Jeff Frost <jeff@pgexperts.com> - 9.3beta1-1PGDG
- Initial cut for 9.3 beta 1

* Wed Apr 17 2013 Devrim GÜNDÜZ <devrim@gunduz.org> - 9.2.4-3PGDG
- Fix pid file name in init script, so that it is more suitable for multiple
  postmasters. Per suggestion from Andrew Dunstan. Fixes #92.

* Thu Apr 11 2013 Devrim GÜNDÜZ <devrim@gunduz.org> - 9.2.4-2PGDG
- Add pg_basebackup to $PATH, per #75.

* Tue Apr 02 2013 Jeff Frost <jeff@pgexperts.com> - 9.2.4-1PGDG
- Update to 9.2.4, per changes described at:
  http://www.postgresql.org/docs/9.2/static/release-9-2-4.html
  which also includes fixes for CVE-2013-1899, CVE-2013-1900, and
  CVE-2013-1901.

* Fri Feb 8 2013 Devrim GÜNDÜZ <devrim@gunduz.org> - 9.2.3-2PGDG
- Fix bug in new installations, that prevents ld.so.conf.d file
  to be installed.

* Wed Feb 6 2013 Devrim GÜNDÜZ <devrim@gunduz.org> - 9.2.3-1PGDG
- Update to 9.2.3, per changes described at:
  http://www.postgresql.org/docs/9.2/static/release-9-2-3.html
- Fix -libs issue while installing 9.1+ in parallel. Per various
  bug reports. Install ld.so.conf.d file with -libs subpackage.
- Move $pidfile and $lockfile definitions before sysconfig call,
  so that they can be included in sysconfig file.

* Thu Dec 6 2012 Devrim GÜNDÜZ <devrim@gunduz.org> - 9.2.2-1PGDG
- Update to 9.2.2, per changes described at:
  http://www.postgresql.org/docs/9.2/static/release-9-2-2.html

* Thu Sep 20 2012 Devrim GÜNDÜZ <devrim@gunduz.org> - 9.2.1-1PGDG
- Update to 9.2.1, per changes described at:
  http://www.postgresql.org/docs/9.2/static/release-9-2-1.html
- Add new functionality: Upgrade from previous version.
  Usage: service postgresql-9.2 upgrade
- Fix version number in initdb warning message, per Jose Pedro Oliveira.

* Thu Sep 6 2012 Devrim GÜNDÜZ <devrim@gunduz.org> - 9.2.0-1PGDG
- Update to 9.2.0
- Split .control files in appropriate packages. This is a late port
  from 9.1 branch. With this patch, pls can be created w/o installing
  -contrib subpackage.
- Re-enable -test subpackage, removed accidentally.

* Tue Aug 28 2012 Devrim GÜNDÜZ <devrim@gunduz.org> - 9.2rc1-2
- Install linker conf file with alternatives, so that the latest 
  version will always be used. Fixes #77.

* Fri Aug 24 2012 Devrim GÜNDÜZ <devrim@gunduz.org> - 9.2rc1-1  
- Update to 9.2 RC1

* Thu Aug 16 2012 Devrim GÜNDÜZ <devrim@gunduz.org> - 9.2beta4-1
- Update to 9.2 beta4, which also includes fixes for CVE-2012-3489 
  and CVE-2012-3488.

* Mon Aug 6 2012 Devrim GÜNDÜZ <devrim@gunduz.org> - 9.2beta3-1
- Update to 9.2 beta3  

* Wed Jun 6 2012 Devrim GÜNDÜZ <devrim@gunduz.org> - 9.2beta2-1
- Update to 9.2 beta2,  which also includes fixes for CVE-2012-2143, 
  CVE-2012-2655.

* Fri May 18 2012 Devrim GÜNDÜZ <devrim@gunduz.org> - 9.2beta1-1
- Initial cut for 9.2 Beta 1
