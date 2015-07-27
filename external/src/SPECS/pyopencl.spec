%include %{_sourcedir}/common.inc

Name:     pyopencl
Version:  2015.1
Release:  1%{?dist}
Summary:  Python wrapper for OpenCL
Source:   %{name}-%{version}.tar.gz
Source1:  common.inc

License:  MIT
Group:    Development/Libraries
URL:      https://pypi.python.org/pypi/pyopencl
BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildRequires: python

%description
PyOpenCL lets you access GPUs and other massively parallel compute devices from Python. It tries to offer computing goodness in the spirit of its sister project PyCUDA:
-Object cleanup tied to lifetime of objects. This idiom, often called RAII in C++, makes it much easier to write correct, leak- and crash-free code.
-Completeness. PyOpenCL puts the full power of OpenCL’s API at your disposal, if you wish. Every obscure get_info() query and all CL calls are accessible.
-Automatic Error Checking. All CL errors are automatically translated into Python exceptions.
-Speed. PyOpenCL’s base layer is written in C++, so all the niceties above are virtually free.
-Helpful and complete Documentation as well as a Wiki.
-Liberal license. PyOpenCL is open-source under the MIT license and free for commercial, academic, and private use.
-Broad support. PyOpenCL was tested and works with Apple’s, AMD’s, and Nvidia’s CL implementations.

%prep
%setup -q -n %{name}-%{version}

%build
 %{__python} configure.py \
  --python-exe=%{__python} \
  --boost-inc-dir=${VIP_INCLUDEDIR} \
  --boost-lib-dir=${VIP_LIBDIR} \
  --boost-python-libname=boost_python \
  --cl-inc-dir=${VIP_OPENCL_INCLUDE_PATH} \
  --cl-lib-dir=${VIP_OPENCL_LIBRARY_PATH} \
  --cl-libname=${VIP_OPENCL_LIBRARY_NAME} \
  --cl-pretend-version=${VIP_OPENCL_VERSION}
#env CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build
make

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --prefix=${RPM_BUILD_ROOT}%{cat_prefix} --install-data=${RPM_BUILD_ROOT}%{_datadir} --single-version-externally-managed --record=/dev/null

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
/
