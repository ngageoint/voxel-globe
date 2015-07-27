%include %{_sourcedir}/common.inc

%global srcname distribute

Name:           setuptools
Version:	15.2
Release:        1%{?dist}
Summary:        Easily build and distribute Python packages

Group:          Applications/System
License:        Python or ZPLv2.0
URL:            http://pypi.python.org/pypi/%{srcname}
Source0:        %{name}-%{version}.tar.gz
Source1:        common.inc
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch
BuildRequires:  python-devel

# Legacy: We removed this subpackage once easy_install no longer depended on
# python-devel
Provides: python-setuptools-devel = %{version}-%{release}
Obsoletes: python-setuptools-devel < 0.6.7-1

# Provide this since some people will request distribute by name
Provides: python-distribute = %{version}-%{release}

%description
Setuptools is a collection of enhancements to the Python distutils that allow
you to more easily build and distribute Python packages, especially ones that
have dependencies on other packages.

This package contains the runtime components of setuptools, necessary to
execute the software that requires pkg_resources.py.

%prep
%setup -q -n %{name}-%{version}
find -name '*.txt' -exec chmod -x \{\} \;
find -name '*.py' -exec sed -i '1s|^#!python|#!%{__python}|' \{\} \;

%build
CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
mkdir -p ${RPM_BUILD_ROOT}/lib/python%{pyver}/site-packages
env PYTHONPATH=${RPM_BUILD_ROOT}%{python_sitelib} %{__python} setup.py install --skip-build --prefix=${RPM_BUILD_ROOT}%{cat_prefix} --install-data=${RPM_BUILD_ROOT}%{_datadir} --single-version-externally-manage --record=/dev/null
rm -rf %{buildroot}%{python_sitelib}/setuptools/tests
rm -rf %{buildroot}%{python_sitelib}/*egg-info/*.orig

find %{buildroot}%{python_sitelib} -name '*.exe' | xargs rm -f
chmod +x %{buildroot}%{python_sitelib}/setuptools/command/easy_install.py

%check
#%{__python} setup.py test I need pytest and py to do the test... Or maybe just internet access IS the test, I don't know

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT


%files
%doc *.txt docs
%{python_sitelib}/*
%{_bindir}/easy_install
%{_bindir}/easy_install-%{pyver}

