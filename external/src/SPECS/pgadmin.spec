%include %{_sourcedir}/common.inc

%global pgmajorversion 93

Name:		pgadmin3
Version:	1.20.0
Release:	1%{?dist}
Summary:	Graphical client for PostgreSQL
Source:		%{name}-%{version}.tar.gz
Source1:        common.inc


License:	BSD
Group:		Applications/Databases
URL: 		http://www.pgadmin.org/
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root
BuildRequires:	wxGTK-devel postgresql%{pgmajorversion}-devel openssl-devel libxml2-devel libxslt-devel
Requires:	wxGTK

%description
pgAdmin III is a powerful administration and development
platform for the PostgreSQL database, free for any use.
It is designed to answer the needs of all users,
from writing simple SQL queries to developing complex
databases. The graphical interface supports all PostgreSQL
features and makes administration easy.

pgAdmin III is designed to answer the needs of all users, 
from writing simple SQL queries to developing complex databases. 
The graphical interface supports all PostgreSQL features and 
makes administration easy. The application also includes a syntax 
highlighting SQL editor, a server-side code editor, an 
SQL/batch/shell job scheduling agent, support for the Slony-I 
replication engine and much more. No additional drivers are 
required to communicate with the database server.

%package docs
Summary:	Documentation for pgAdmin3
Group:		Applications/Databases
Requires:	%{name}_%{pgmajorversion} = %{version}

%description docs
This package contains documentation for various languages,
which are in html format.

%prep
%setup -q -n %{name}-%{version}

%build
#export LIBS=-lwx_gtk2u_core-3.0
./configure --with-pgsql=%{install_dir}%{cat_prefix} --with-wx=%{install_dir}%{_prefix} --with-wx-version=3.0 --prefix=%{_prefix} --disable-debug --disable-dependency-tracking 

make %{?_smp_mflags} all

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
%makeinstall

mkdir -p %{buildroot}%{_datadir}/%{name}/
cp -f ./pkg/debian/pgadmin3.xpm %{buildroot}/%{_datadir}/%{name}/%{name}.xpm

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-, root, root)
%doc BUGS CHANGELOG LICENSE README
%{_bindir}
#%{_datadir}/%{name}

%files docs
%defattr(-,root,root)
#%doc docs/*
%{_datadir}

%changelog
* Tue Nov 19 2013 Devrim GUNDUZ <devrim@gunduz.org> 1.18.1-2
- Fix file paths, per #118.
- Fix alternatives version.

* Tue Oct 8 2013 Devrim GUNDUZ <devrim@gunduz.org> 1.18.1-1
- Update to 1.18.1     

* Fri Aug 30 2013 Devrim GUNDUZ <devrim@gunduz.org> 1.18.0-1
- Update to 1.18.0 Gold

* Mon Feb 11 2013 Devrim GÜNDÜZ <devrim@gunduz.org> - 1.16.1-4
- More fixes to the %%preun section.

* Fri Jan 25 2013 Devrim GÜNDÜZ <devrim@gunduz.org> - 1.16.1-3
- Fix typo in init script.

* Wed Jan 23 2013 Devrim GÜNDÜZ <devrim@gunduz.org> - 1.16.1-2
- Fix %%post and %%postin issues.

* Mon Dec 10 2012 Devrim GUNDUZ <devrim@gunduz.org> 1.16.1-1
- Update to 1.16.1     

* Thu Sep 6 2012 Devrim GUNDUZ <devrim@gunduz.org> 1.16.0-1
- Update to 1.16.0 Gold

* Tue Nov 15 2011 Devrim GÜNDÜZ <devrim@gunduz.org> - 1.14.0-3
- Fix paths in desktop file paths, per Stephen Blake. Also bump up the
  alternatives version..

* Mon Oct 31 2011 Devrim GÜNDÜZ <devrim@gunduz.org> - 1.14.0-2
-  Fix desktop file. Patch from Kim Bisgaard.

* Fri Sep 9 2011 Devrim GUNDUZ <devrim@gunduz.org> 1.14.0-1
- Update to 1.14.0 Gold

* Fri Apr 15 2011 Devrim GUNDUZ <devrim@gunduz.org> 1.12.3-1
- Update to 1.12.3

* Tue Dec 14 2010 Devrim GUNDUZ <devrim@gunduz.org> 1.12.2-2
- Update to 1.12.2

* Thu Oct 7 2010 Devrim GUNDUZ <devrim@gunduz.org> 1.12.1-1
- Update to 1.12.1

* Mon Sep 20 2010 Devrim GUNDUZ <devrim@gunduz.org> 1.12.0-1
- Update to 1.12.0
- Apply multiple postmaster specific changes and patch.
- Trim changelog.

* Tue Mar 9 2010 Devrim GUNDUZ <devrim@gunduz.org> 1.10.2-1
- Update to 1.10.2
- Improve configure line to support new multiple postmaster installation
  feature.

* Sat Dec 5 2009 Devrim GUNDUZ <devrim@gunduz.org> 1.10.1-1
- Update to 1.10.1

* Mon Jun 29 2009 Devrim GUNDUZ <devrim@gunduz.org> 1.10.0
- Update to 1.10.0 Gold

* Wed Mar 25 2009 Devrim GUNDUZ <devrim@gunduz.org> 1.10.0-beta2
- Update to 1.10.0 beta2

* Fri Mar 13 2009 Devrim GUNDUZ <devrim@gunduz.org> 1.10.0-beta1
- Update to 1.10.0 beta1
- Update patch0

* Tue Jul 15 2008 Devrim GUNDUZ <devrim@gunduz.org> 1.8.4-2
- Use $RPM_OPT_FLAGS, build with dependency tracking disabled 
(#229054). Patch from Ville Skyttä

* Thu Jun 5 2008 Devrim GUNDUZ <devrim@gunduz.org> 1.8.4-1
- Update to 1.8.4

* Tue Jun 3 2008 Devrim GUNDUZ <devrim@gunduz.org> 1.8.3-1
- Update to 1.8.3

* Fri Feb 1 2008 Devrim GUNDUZ <devrim@gunduz.org> 1.8.2-1
- Update to 1.8.2

* Fri Jan 4 2008 Devrim GUNDUZ <devrim@gunduz.org> 1.8.1-1
- Update to 1.8.1

* Wed Dec 05 2007 Devrim GUNDUZ <devrim@gunduz.org> 1.8.0-2
- Rebuild for openssl bump

