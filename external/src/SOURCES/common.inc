Prefix: /
%define _smp_mflags      -j`nproc`

#This is primarily for NON-rhel oses where sh and bash do not behave the same, and since most of my spec files are bash ...
%define ___build_shell %(which bash)

#For other oses that do not have /etc/rpm/macros defined specifically for that os
%if 0%{?fedora}==0 && 0%{?rhel}==0 && 0%{?suse}==0
  %if "%(test -e /etc/lsb-release; echo $?)" == "0"
    %define __lsb_os %(. /etc/lsb-release; echo ${DISTRIB_ID})
    %if "%{__lsb_os}" == "Ubuntu"
      %define ubuntu %(. /etc/lsb-release; perl -MPOSIX -e "print floor(${DISTRIB_RELEASE})")
    %else
    %if "%{__lsb_os}" == "LinuxMint"
      %define mint %(. /etc/lsb-release; perl -MPOSIX -e "print floor(${DISTRIB_RELEASE})")
    %else
      echo "Unknown OS %{__lsb_os}. Please add to common.inc and other SPEC"
    %endif %endif
    %endif
  %else
    echo Cannot determine OS. Please add to common.inc and other SPEC
  %endif
%endif

%define project_root     %(echo ${VIP_PROJECT_ROOT})
%define install_dir      %(echo ${VIP_INSTALL_DIR})

%define opencl_include_dir %(echo %{VIP_OPENCL_INCLUDE_PATH})
%define opencl_libflags    %(echo %{VIP_OPENCL_LIBRARY_FLAGS})
#%define tclconfig_dir      /usr/lib64

%define _prefix          %(echo ${VIP_PREFIX_BASE-/})

%if "%{_prefix}" == "/"
  %define cat_prefix %{nil}
  %define re_prefix /
  #Special for Postgres because it actually tried to be portable, but need the // to figure it out
%else
  %define cat_prefix %{_prefix}
  %define re_prefix %{nil}
%endif

%define _exec_prefix     %(echo ${VIP_EXECPREFIX_BASE-%{prefix}})

%define _bindir          %(echo ${VIP_BINDIR_BASE-%{cat_prefix}/bin})
%define _datadir         %(echo ${VIP_DATADIR_BASE-%{cat_prefix}/share})
%define _includedir      %(echo ${VIP_INCLUDEDIR_BASE-%{cat_prefix}/include})
%define _libdir          %(echo ${VIP_LIBDIR_BASE-%{cat_prefix}/lib})
%define _libexecdir      %(echo ${VIP_LIBEXECDIR_BASE-%{cat_prefix}/libexec})
%define _localstatedir   %(echo ${VIP_LOCALSTATEDIR_BASE-%{cat_prefix}/var})
%define _sbindir         %(echo ${VIP_SBINDIR_BASE-%{cat_prefix}/sbin})
%define _sysconfdir      %(echo ${VIP_SYSCONFDIR_BASE-%{cat_prefix}/etc})
%define _sharedstatedir  %(echo ${VIP_SHAREDSTATEDIR_BASE-%{_datadir}/com})

%define _docdir          %(echo ${VIP_DOCDIR_BASE-%{_datadir}/doc})
%define _infodir         %(echo ${VIP_INFODIR_BASE-%{_datadir}/info})
%define _mandir          %(echo ${VIP_MANDIR_BASE-%{_datadir}/man})

%define _roamdir         %(echo ${VIP_ROAM_DIR-%{install_dir}/roam})

%define _debugdir        %(echo ${VIP_DEBUGDIR_DIR-/usr/lib/debug})
#Useful for excluding

%global __python         %{_roamdir}/python

%global __cmake          %(echo ${VIP_CMAKE-cmake})

%global _python_bytecompile_errors_terminate_build 0

%define add_install_flags export LDFLAGS=${LDFLAGS:+${LDFLAGS} }-L%{install_dir}%{_libdir} \
export CFLAGS=${CFLAGS:+${CFLAGS} }-I%{install_dir}%{_includedir} \
export CPPFLAGS=${CPPFLAGS:+${CPPFLAGS} }-I%{install_dir}%{_includedir} \
export LD_LIBRARY_PATH=%{install_dir}%{_libdir}${LD_LIBRARY_PATH:+ ${LD_LIBRARY_PATH}}

%define add_install_path export PATH=%{_roamdir}${PATH:+:${PATH}}
#Useful for /usr/bin/env python scripts

%define add_current_ld export LD_LIBRARY_PATH="$RPM_BUILD_ROOT"/lib${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}

### Global application specific variables ###
%define httpd_moddir %(echo ${VIP_HTTPD_SERVERROOT_BASE-%{_libdir}/httpd}/modules)
%define httpd_contentdir %{_localstatedir}/www

%define postgresql_libdir %{_libdir}/postgresql
%define postgresql_includedir %{_includedir}/postgresql

### Ppython Magic helper :)

%if "%(test -e %{__python}; echo $?)" == "0"
#This stupid if is just to supress error messages that would pop up when generating the SRPMS
  #These are good for libdir=%{_prefix}%{lib_prefix_rel}
  %{!?bin_prefix_rel:                 %define bin_prefix_rel %(%{__python} -c "import os.path; print os.path.relpath('%{_bindir}',        '%{_prefix}')")}
  %{!?data_prefix_rel:               %define data_prefix_rel %(%{__python} -c "import os.path; print os.path.relpath('%{_datadir}',       '%{_prefix}')")}
  %{!?exec_prefix_prefix_rel: %define exec_prefix_prefix_rel %(%{__python} -c "import os.path; print os.path.relpath('%{_exec_prefix}',   '%{_prefix}')")}
  %{!?include_prefix_rel:         %define include_prefix_rel %(%{__python} -c "import os.path; print os.path.relpath('%{_includedir}',    '%{_prefix}')")}
  %{!?lib_prefix_rel:                 %define lib_prefix_rel %(%{__python} -c "import os.path; print os.path.relpath('%{_libdir}',        '%{_prefix}')")}
  %{!?localstate_prefix_rel:   %define localstate_prefix_rel %(%{__python} -c "import os.path; print os.path.relpath('%{_localstatedir}', '%{_prefix}')")}
  %{!?man_prefix_rel:                 %define man_prefix_rel %(%{__python} -c "import os.path; print os.path.relpath('%{_mandir}',        '%{_prefix}')")}
  %{!?sysconf_prefix_rel:         %define sysconf_prefix_rel %(%{__python} -c "import os.path; print os.path.relpath('%{_sysconfdir}',    '%{_prefix}')")}

  #Special case for wxWidgets :-\
  %{!?lib_bin_rel:                       %define lib_bin_rel %(%{__python} -c "import os.path; print os.path.relpath('%{_libdir}',        '%{_bindir}')")}

  #These are good for prefix=VIP_BINDIR/%{bin_prefix_rel}
  %{!?exec_prefix_bin_rel:       %define exec_prefix_bin_rel %(%{__python} -c "import os.path; print os.path.relpath('%{_exec_prefix}',   '%{_bindir}')")}
  %{!?prefix_bin_rel:                 %define prefix_bin_rel %(%{__python} -c "import os.path; print os.path.relpath('%{_prefix}',        '%{_bindir}')")}
  %{!?prefix_lib_rel:                 %define prefix_lib_rel %(%{__python} -c "import os.path; print os.path.relpath('%{_prefix}',        '%{_libdir}')")}

  #Common by some python packages
  %define pyver %(%{__python} -c "import sys ; print sys.version[:3]")
  %define python_sitearch /%(%{__python} -c "from distutils.sysconfig import get_python_lib; import os.path; print os.path.relpath(get_python_lib(1), '%{install_dir}')")
  %define python_sitelib  /%(%{__python} -c "from distutils.sysconfig import get_python_lib; import os.path; print os.path.relpath(get_python_lib(), '%{install_dir}')")

  #Special cases
  %{!?httpd_content_prefix_rel: %define httpd_content_prefix_rel %(%{__python} -c "import os.path; print os.path.relpath('%{httpd_contentdir}', '%{_prefix}')")}
%else
 %define python_sitearch %{nil}
 %define python_sitelib %{nil}
 %define pyver %{nil}
%endif

