%include %{_sourcedir}/common.inc

Summary: Python Imaging Library (Fork)
Name: Pillow
Version:	2.8.1
Release: 1%{?dist}
Source0: %{name}-%{version}.zip
Source1: common.inc
License: Standard PIL License
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Vendor: Alex Clark (fork author) <aclark@aclark.net>
URL: http://python-imaging.github.io/

BuildRequires: lcms2-devel
BuildRequires: openjpeg-devel
Requires:      lcms2-libs
Requires:      openjpeg-libs

%description
Pillow
======

*Python Imaging Library (Fork)*

Pillow is the "friendly" PIL fork by Alex Clark and Contributors. PIL is the Python Imaging Library by Fredrik Lundh and Contributors.

.. image:: https://travis-ci.org/python-imaging/Pillow.png
   :target: https://travis-ci.org/python-imaging/Pillow

.. image:: https://pypip.in/v/Pillow/badge.png
    :target: https://pypi.python.org/pypi/Pillow/
    :alt: Latest PyPI version

.. image:: https://pypip.in/d/Pillow/badge.png
    :target: https://pypi.python.org/pypi/Pillow/
    :alt: Number of PyPI downloads

The documentation is hosted at http://pillow.readthedocs.org/. It contains installation instructions, tutorials, reference, compatibility details, and more.

%prep
%setup -n %{name}-%{version}

%build
env CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install --single-version-externally-managed -O1 --record=INSTALLED_FILES --prefix=${RPM_BUILD_ROOT}%{cat_prefix} --install-data=${RPM_BUILD_ROOT}%{_datadir}

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
%exclude /usr/lib/debug
/
