%include %{_sourcedir}/common.inc

Summary: Python 2 and 3 compatibility utilities
Name: six
Version: 1.9.0
Release: 1%{?dist}
Source0: %{name}-%{version}.tar.gz
Source1: common.inc
License: Standard PIL License
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildArch: noarch
Vendor: Benjamin Peterson <benjamin@python.org>
URL: http://pypi.python.org/pypi/six/

BuildRequires: lcms2-devel
BuildRequires: openjpeg-devel
Requires:      lcms2-libs
Requires:      openjpeg-libs

%description
Six is a Python 2 and 3 compatibility library.  It provides utility functions
for smoothing over the differences between the Python versions with the goal of
writing Python code that is compatible on both Python versions.  See the
documentation for more information on what is provided.

Six supports every Python version since 2.5.  It is contained in only one Python
file, so it can be easily copied into your project. (The copyright and license
notice must be retained.)

Online documentation is at http://pythonhosted.org/six/.

Bugs can be reported to http://bitbucket.org/gutworth/six.  The code can also be
found there.

For questions about six or porting in general, email the python-porting mailing
list: http://mail.python.org/mailman/listinfo/python-porting

%prep
%setup -n %{name}-%{version}

%build
env CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install --single-version-externally-managed -O1 --record=/dev/null --prefix=${RPM_BUILD_ROOT}%{cat_prefix} --install-data=${RPM_BUILD_ROOT}%{_datadir}

%check
#%{__python}
#  cd ${PIL_SRC_DIR[${#PIL_SRC_DIR[@]}-1]}
#  ${PYTHON} ./setup.py develop >> $CHECK_FILE
#  ${PYTHON} ./setup.py test >> $CHECK_FILE
#  ${PYTHON} ./selftest.py >> $CHECK_FILE
#  ${CONTINUE_ON_ERROR}
#  ${PYTHON} ./Tests/run.py --installed || exit(0)

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
/
