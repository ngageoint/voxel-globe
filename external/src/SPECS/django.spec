%include %{_sourcedir}/common.inc

Name:		Django
Version:	1.8.1
Release:	1%{?dist}
Summary:	The Web framework for perfectionists with deadlines
Source:		%{name}-%{version}.tar.gz
Source1:	python-django.conf
Source2:	python-django.wsgi
Source3:        common.inc

License:	BSD
Group:		Development/Languages
URL: 		http://www.djangoproject.com/
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root
BuildRequires:  python
Requires:       python
BuildArch: 	noarch

%description
Django is a high-level Python Web framework that encourages rapid development
and clean, pragmatic design.

Developed four years ago by a fast-moving online-news operation, Django was
designed to handle two challenges: the intensive deadlines of a newsroom and
the stringent requirements of the experienced Web developers who wrote it. It
lets you build high-performing, elegant Web applications quickly.

%package integration-apache
Summary: The Web framework for perfectionists with deadlines (Apache integration)
Group: Development/Languages
Requires: %{name} = %{version}-%{release}

# Apache web server, obviously
Requires: httpd

# Corresponding Apache modules
%{?el5:Requires: mod_python}
%{?el6:Requires: mod_wsgi}

# MySQL (ships with RHEL)
Requires: MySQL-python

# PostgreSQL (RepoForge for RHEL <=5, stock for RHEL6)
Requires: python-psycopg2

# SQLite (RepoForge for RHEL5, stock for RHEL6)
%{?el5:Requires: python-sqlite2}
%{?el6:Requires: python-sqlite}

%description integration-apache
This package provides Apache integration for Django.

%prep
%setup -q -n %{name}-%{version}

%build
env CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --prefix=${RPM_BUILD_ROOT}%{cat_prefix} --install-data=${RPM_BUILD_ROOT}%{_datadir} --single-version-externally-managed --record=/dev/null

# Handling locale files
(cd %{buildroot} && find . -name 'django*.mo') | %{__sed} -e 's|^.||' | %{__sed} -e \
    's:\(.*/locale/\)\([^/_]\+\)\(.*\.mo$\):%lang(\2) \1\2\3:' \
    >> %{name}.lang

# install man pages
mkdir -p %{buildroot}%{_mandir}/man1/
cp -p docs/man/* %{buildroot}%{_mandir}/man1/

# Fix items in %%{_bindir}
mv %{buildroot}%{_bindir}/django-admin.py %{buildroot}%{_bindir}/django-admin

# remove .po files
find %{buildroot} -name "*.po" | xargs rm -f

# Fix permissions
chmod 755 \
    %{buildroot}%{python_sitelib}/django/bin/django-admin.py \
    %{buildroot}%{python_sitelib}/django/conf/project_template/manage.py

# Bash completion
#install -d %{buildroot}%{_sysconfdir}/bash_completion.d/
#install -m 0644 extras/django_bash_completion %{buildroot}%{_sysconfdir}/bash_completion.d/django
#rm extras/django_bash_completion

# Install the Apache config
%{__install} -m0755 -d %{buildroot}%{_sysconfdir}/httpd/conf.d/django
%{__install} -m0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/httpd/conf.d/django.conf
%{__install} -m0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/httpd/conf.d/django/default.wsgi

# Make a directory to hold Django apps
%{__install} -m0755 -d %{buildroot}%{_localstatedir}/www/django/


%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-, root, root, 0755)
%doc AUTHORS LICENSE PKG-INFO README.rst
%doc docs/ extras/
%{_bindir}/django-admin
%{_mandir}/man1/*
#%config %{_sysconfdir}/bash_completion.d/django
%{python_sitelib}/django/
%{!?_without_egginfo:%{python_sitelib}/*.egg-info}

%files integration-apache
%defattr(-, root, root, 0755)
%config(noreplace) %{_sysconfdir}/httpd/conf.d/django.conf
%config(noreplace) %{_sysconfdir}/httpd/conf.d/django/default.wsgi
%{_localstatedir}/www/django/

%changelog
* Tue Sep 27 2011 Yury V. Zaytsev <yury@shurup.com> - 1.3.1-1
- Updated to release 1.3.1.
- Split Apache integration files in a sub-package.

* Thu Oct 21 2010 Steve Huff <shuff@vecna.org> - 1.2.3-1
- Updated to version 1.2.3.
- No more examples/ directory.

* Tue Sep 21 2010 Steve Huff <shuff@vecna.org> - 1.1.1-2
- Renamed package to python-django.
- Removed mod_python dependency per Yury's suggestion.
- Django sites live in /var/www/django.

* Tue Apr 27 2010 Steve Huff <shuff@vecna.org> - 1.1.1-1
- Initial package.


