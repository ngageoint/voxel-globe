%include %{_sourcedir}/common.inc

Name:		json-c
Version:	0.12
Release:	1%{?dist}
Summary:	JSON C class
Source:		%{name}-%{version}.tar.gz
Source1:    common.inc
Patch0:    %{name}-%{version}.patch
License:	MIT License
Group:		Applications/Engineering
URL: 		https://github.com/json-c/json-c/wiki
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root
BuildRequires:  autoconf automake libtool

%description
JSON-C implements a reference counting object model that allows you to easily construct JSON objects in C, output them as JSON formatted strings and parse JSON formatted strings back into the C representation of JSON objects.

%prep
%setup -q -n %{name}-%{version}
%patch0 -p1

%build
autoreconf --force --install
%configure

make %{_smp_mflags}

%check
LD_LIBRARY_PATH=`pwd`${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
export LD_LIBRARY_PATH
make check %{_smp_mflags}

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
%makeinstall

mkdir -p $RPM_BUILD_ROOT%{_libdir}/la
mv $RPM_BUILD_ROOT%{_libdir}/*.la $RPM_BUILD_ROOT%{_libdir}/la

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%exclude /usr/lib/debug
/

%post

%postun

