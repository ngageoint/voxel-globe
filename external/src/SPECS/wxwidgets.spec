%include %{_sourcedir}/common.inc

%define ver  3.0.2
%define ver2 3.0
%define rel  1

# Configurable settings (use --with(out) {unicode,gtk2} on rpmbuild cmd line):
%define unicode 1
%{?_with_unicode: %{expand: %%define unicode 1}}
%{?_without_unicode: %{expand: %%define unicode 0}}

%define gtk2 1
%{?_with_gtk2: %{expand: %%define gtk2 1}}
%{?_without_gtk2: %{expand: %%define gtk2 0}}

# "buildname" needs to be e.g. gtk2ud for debug builds
%if %{gtk2}
    %define gtkver 2
    %define portname gtk2
%if %{unicode}
    %define buildname gtk2u
%else
    %define buildname gtk2
%endif
%else
    %define gtkver 1.2
    %define portname gtk
    %define buildname gtk
%endif

%if %{unicode}
    %define name		wx-%{portname}-unicode
    %define wxconfig		%{portname}-unicode-%{ver2}
    %define wxconfigstatic	%{portname}-unicode-static-%{ver2}
    %define wxconfiglink	wx%{portname}u-%{ver2}-config
%else
    %define name		wx-%{portname}-ansi
    %define wxconfig		%{portname}-ansi-%{ver2}
    %define wxconfigstatic	%{portname}-ansi-static-%{ver2}
    %define wxconfiglink	wx%{portname}-%{ver2}-config
%endif

%if %{unicode}
    %define wxbasename		wx-base-unicode
    %define wxbaseconfig	base-unicode-%{ver2}
    %define wxbaseconfiglink	wxbaseu-%{ver2}-config
%else
    %define wxbasename		wx-base-ansi
    %define wxbaseconfig	base-ansi-%{ver2}
    %define wxbaseconfiglink	wxbase-%{ver2}-config
%endif

Name:		wxWidgets
Version:	3.0.2
Release:	1%{?dist}
Summary:	The GTK+ %{version} port of the wxWidgets library
Source:		%{name}-%{version}.tar.bz2
Source1:        common.inc
License:	wxWindows License
Group:		11/Libraries
URL:            http://www.wxwidgets.org
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root
Requires: %{wxbasename} = %{ver}
%if %{portname} == gtk2
BuildRequires: gtk2-devel
%else
BuildRequires: gtk+-devel >= 1.2.0
%endif

%if 0%{?suse_version}
BuildRequires: zlib-devel, gstreamer-0_10-devel, gstreamer-0_10-plugins-base-devel, gconf2-devel, libwebkitgtk-devel >= 1.3.1
%else
%if 0%{?fedora}
BuildRequires: zlib-devel, gstreamer-devel, gstreamer-plugins-base-devel, GConf2-devel, webkitgtk-devel >= 1.3.1
%else
# CentOS, RedHat etc. CentOS (at least) doesn't have a sufficiently recent webkit for webview. I don't know about mandriva/mageia
BuildRequires: zlib-devel, gstreamer-devel, gstreamer-plugins-base-devel, GConf2-devel
%endif
%endif

Provides: wxwin
Provides: wxGTK

%description
wxWidgets is a free C++ library for cross-platform GUI development.
With wxWidgets, you can create applications for different GUIs (GTK+,
Motif, MS Windows, MacOS X, Windows CE, GPE) from the same source code.

%package -n wx-i18n
Summary: The translations for the wxWidgets library.
Group: X11/Libraries

%description -n wx-i18n
The translations files for the wxWidgets library.

%package devel
Summary: The GTK+ %{gtkver} port of the wxWidgets library
Group: X11/Libraries
Requires: %{name} = %{ver}
Requires: %{wxbasename}-devel = %{ver}
Provides: wxGTK-devel

%description devel
The GTK+ %{gtkver} port of the wxWidgets library, header files.

%package gl
Summary: The GTK+ %{gtkver} port of the wxWidgets library, OpenGL add-on.
Group: X11/Libraries
Requires: %{name} = %{ver}
Provides: wxGTK-gl

%description gl
OpenGL add-on library for wxGTK, the GTK+ %{gtkver} port of the wxWidgets library.

%package -n %{wxbasename}
Summary: wxBase library - non-GUI support classes of the wxWidgets toolkit
Group: Development/Libraries
Provides: wxBase

%description -n %{wxbasename}
wxBase is a collection of C++ classes providing basic data structures (strings,
lists, arrays), portable wrappers around many OS-specific funstions (file
operations, time/date manipulations, threads, processes, sockets, shared
library loading) as well as other utility classes (streams, archive and
compression). wxBase currently supports Win32, most Unix variants (Linux,
FreeBSD, Solaris, HP-UX) and MacOS X (Carbon and Mach-0).

%package -n %{wxbasename}-devel
Summary: wxBase library, header files.
Group: Development/Libraries
Provides: wxBase-devel

%description -n %{wxbasename}-devel
wxBase library - non-GUI support classes of the wxWidgets toolkit,
header files.

%prep
%setup -q -n %{name}-%{version}

sed -i 's|^#!/bin/sh$|#!/usr/bin/env bash|' wx-config.in
sed -i 's|@prefix@|$(cd $(dirname $(readlink -f ${BASH_SOURCE[0]}))/../../%{prefix_lib_rel}; pwd)|' wx-config.in
sed -i 's|@libdir@|${prefix}/%{lib_prefix_rel}|' wx-config.in

%build

if [ "$SMP" != "" ]; then
    export MAKE="make -j$SMP"
else
    export MAKE="make"
fi

mkdir obj-shared
cd obj-shared
../configure --prefix=%{_prefix} --libdir=%{_libdir} \
%if ! %{gtk2}
			      --with-gtk=1 \
%else
			      --with-gtk=2 \
%endif
%if %{unicode}
			      --enable-unicode \
%else
			      --disable-unicode \
%endif
			      --with-opengl \
			      --with-gnomeprint \
			      --with-libjpeg=builtin  --with-libpng=builtin  --with-libtiff=builtin \
			      --with-zlib=builtin  --with-expat=builtin
$MAKE %{_smp_mflags}
#			      --enable-mediactrl \

cd ..

mkdir obj-static
cd obj-static
../configure --prefix=%{_prefix} --libdir=%{_libdir} \
%if ! %{gtk2}
			      --with-gtk=1 \
%else
			      --with-gtk=2 \
%endif
			      --disable-shared \
%if %{unicode}
			      --enable-unicode \
%else
			      --disable-unicode \
%endif
			      --with-opengl \
			      --with-gnomeprint \
			      --with-libjpeg=builtin  --with-libpng=builtin  --with-libtiff=builtin \
			      --with-zlib=builtin  --with-expat=builtin
$MAKE %{_smp_mflags}
#			      --enable-mediactrl \

cd ..

make -C locale allmo %{_smp_mflags}

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
(cd obj-static; make DESTDIR=$RPM_BUILD_ROOT prefix=%{_prefix} install)
(cd obj-shared; make DESTDIR=$RPM_BUILD_ROOT prefix=%{_prefix} install)

# --- wxBase headers list begins here ---
cat <<EOF >wxbase-headers.files
wx/afterstd.h
wx/any.h
wx/anystr.h
wx/app.h
wx/apptrait.h
wx/archive.h
wx/arrimpl.cpp
wx/arrstr.h
wx/atomic.h
wx/base64.h
wx/beforestd.h
wx/buffer.h
wx/build.h
wx/chartype.h
wx/checkeddelete.h
wx/chkconf.h
wx/clntdata.h
wx/cmdargs.h
wx/cmdline.h
wx/confbase.h
wx/config.h
wx/convauto.h
wx/containr.h
wx/cpp.h
wx/crt.h
wx/datetime.h
wx/datstrm.h
wx/dde.h
wx/debug.h
wx/defs.h
wx/dir.h
wx/dlimpexp.h
wx/dlist.h
wx/dynarray.h
wx/dynlib.h
wx/dynload.h
wx/encconv.h
wx/event.h
wx/eventfilter.h
wx/evtloop.h
wx/except.h
wx/features.h
wx/flags.h
wx/ffile.h
wx/file.h
wx/fileconf.h
wx/filefn.h
wx/filename.h
wx/filesys.h
wx/fontenc.h
wx/fontmap.h
wx/fs_arc.h
wx/fs_filter.h
wx/fs_mem.h
wx/fs_zip.h
wx/hash.h
wx/hashmap.h
wx/hashset.h
wx/html/forcelnk.h
wx/iconloc.h
wx/init.h
wx/intl.h
wx/iosfwrap.h
wx/ioswrap.h
wx/ipc.h
wx/ipcbase.h
wx/kbdstate.h
wx/language.h
wx/link.h
wx/list.h
wx/listimpl.cpp
wx/log.h
wx/longlong.h
wx/math.h
wx/memconf.h
wx/memory.h
wx/memtext.h
wx/mimetype.h
wx/module.h
wx/mousestate.h
wx/msgout.h
wx/msgqueue.h
wx/mstream.h
wx/numformatter.h
wx/object.h
wx/platform.h
wx/platinfo.h
wx/power.h
wx/process.h
wx/ptr_scpd.h
wx/ptr_shrd.h
wx/recguard.h
wx/regex.h
wx/rtti.h
wx/scopedarray.h
wx/scopedptr.h
wx/scopeguard.h
wx/sharedptr.h
wx/snglinst.h
wx/sstream.h
wx/stack.h
wx/stackwalk.h
wx/stdpaths.h
wx/stdstream.h
wx/stockitem.h
wx/stopwatch.h
wx/strconv.h
wx/stream.h
wx/string.h
wx/stringimpl.h
wx/stringops.h
wx/strvararg.h
wx/sysopt.h
wx/tarstrm.h
wx/textbuf.h
wx/textfile.h
wx/thread.h
wx/thrimpl.cpp
wx/time.h
wx/timer.h
wx/tls.h
wx/tokenzr.h
wx/tracker.h
wx/translation.h
wx/txtstrm.h
wx/typeinfo.h
wx/types.h
wx/unichar.h
wx/uri.h
wx/ustring.h
wx/utils.h
wx/variant.h
wx/vector.h
wx/version.h
wx/versioninfo.h
wx/volume.h
wx/weakref.h
wx/wfstream.h
wx/wx.h
wx/wxchar.h
wx/wxcrt.h
wx/wxcrtbase.h
wx/wxcrtvararg.h
wx/wxprec.h
wx/xlocale.h
wx/xti.h
wx/xti2.h
wx/xtistrm.h
wx/xtictor.h
wx/xtihandler.h
wx/xtiprop.h
wx/xtitypes.h
wx/zipstrm.h
wx/zstream.h
wx/meta/convertible.h
wx/meta/if.h
wx/meta/implicitconversion.h
wx/meta/int2type.h
wx/meta/movable.h
wx/meta/pod.h
wx/fswatcher.h
wx/generic/fswatcher.h
wx/unix/app.h
wx/unix/apptbase.h
wx/unix/apptrait.h
wx/unix/chkconf.h
wx/unix/evtloop.h
wx/unix/evtloopsrc.h
wx/unix/pipe.h
wx/unix/stdpaths.h
wx/unix/stackwalk.h
wx/unix/tls.h
wx/unix/fswatcher_kqueue.h
wx/unix/execute.h
wx/unix/mimetype.h
wx/unix/fswatcher_inotify.h
wx/fs_inet.h
wx/protocol/file.h
wx/protocol/ftp.h
wx/protocol/http.h
wx/protocol/log.h
wx/protocol/protocol.h
wx/sckaddr.h
wx/sckipc.h
wx/sckstrm.h
wx/socket.h
wx/url.h
wx/xml/xml.h
wx/xtixml.h
EOF
# --- wxBase headers list ends here ---

# --- wxBase headers list with paths ---
sed -e 's@^@%{_includedir}/wx-%{ver2}/@' wxbase-headers.files > wxbase-headers.paths


# temporarily remove base headers
mkdir $RPM_BUILD_ROOT/_save_dir
cp -r $RPM_BUILD_ROOT%{_includedir}/wx-%{ver2} $RPM_BUILD_ROOT/_save_dir
for f in `cat wxbase-headers.files` ; do
    rm -f $RPM_BUILD_ROOT%{_includedir}/wx-%{ver2}/$f
done
# list of all core headers:
find $RPM_BUILD_ROOT%{_includedir}/wx-%{ver2} -type f | sed -e "s,$RPM_BUILD_ROOT,,g" >core-headers.files
# move base headers (actually all headers) back again
cp -f -r $RPM_BUILD_ROOT/_save_dir/* $RPM_BUILD_ROOT%{_includedir}
rm -rf $RPM_BUILD_ROOT/_save_dir

# utils:
(cd obj-shared/utils/wxrc; make DESTDIR=$RPM_BUILD_ROOT prefix=%{_prefix} install)

# wx-config link is created during package installation, remove it for now
rm -f $RPM_BUILD_ROOT%{_bindir}/wx-config

%if %{unicode}
    #cp -f ${RPM_BUILD_ROOT}%{_libdir}/wx/config/%{wxconfig} ${RPM_BUILD_ROOT}%{_bindir}/wx-config
    #ln -sf `%{__python} -c "import os.path; print os.path.relpath('%{_libdir}/wx/config/', '%{_bindir}')"`%{wxconfig} wx-config
    ln -sf %{lib_bin_rel}/wx/config/%{wxconfig} ${RPM_BUILD_ROOT}%{_bindir}/wx-config    
%endif
# link wx-config with explicit name.
#cp -f ${RPM_BUILD_ROOT}%{_libdir}/wx/config/%{wxconfig} ${RPM_BUILD_ROOT}%{_bindir}/%{wxconfiglink}
#ln -sf `%{__python} -c "import os.path; print os.path.relpath('%{_libdir}/wx/config/', '%{_bindir}')"`%{wxconfig} %{wxconfiglink}
ln -sf %{lib_bin_rel}/wx/config/%{wxconfig} ${RPM_BUILD_ROOT}%{_bindir}/%{wxconfiglink}

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%doc docs/*.txt
%{_libdir}/libwx_%{buildname}_adv-%{ver2}.so.*
%{_libdir}/libwx_%{buildname}_aui-%{ver2}.so.*
%{_libdir}/libwx_%{buildname}_core-%{ver2}.so.*
%{_libdir}/libwx_%{buildname}_html-%{ver2}.so.*
#%{_libdir}/libwx_%{buildname}_media-%{ver2}.so.*
%{_libdir}/libwx_%{buildname}_propgrid-%{ver2}.so.*
%{_libdir}/libwx_%{buildname}_qa-%{ver2}.so.*
%{_libdir}/libwx_%{buildname}_ribbon-%{ver2}.so.*
%{_libdir}/libwx_%{buildname}_richtext-%{ver2}.so.*
%{_libdir}/libwx_%{buildname}_stc-%{ver2}.so.*
%{_libdir}/libwx_%{buildname}_xrc-%{ver2}.so.*
%if 0%{?fedora} || 0%{?suse_version}
%{_libdir}/libwx_%{buildname}_webview-%{ver2}.so.*
%endif
%{_libdir}/libwxpng-%{ver2}.a
%{_libdir}/libwxtiff-%{ver2}.a
%{_libdir}/libwxjpeg-%{ver2}.a

%files -n wx-i18n
%{_datadir}/locale/*/LC_MESSAGES/*.mo

%files devel -f core-headers.files
# shared libs
%{_libdir}/libwx_%{buildname}_adv-%{ver2}.so
%{_libdir}/libwx_%{buildname}_aui-%{ver2}.so
%{_libdir}/libwx_%{buildname}_core-%{ver2}.so
%{_libdir}/libwx_%{buildname}_gl-%{ver2}.so
%{_libdir}/libwx_%{buildname}_html-%{ver2}.so
#%{_libdir}/libwx_%{buildname}_media-%{ver2}.so
%{_libdir}/libwx_%{buildname}_propgrid-%{ver2}.so
%{_libdir}/libwx_%{buildname}_qa-%{ver2}.so
%{_libdir}/libwx_%{buildname}_ribbon-%{ver2}.so
%{_libdir}/libwx_%{buildname}_richtext-%{ver2}.so
%{_libdir}/libwx_%{buildname}_stc-%{ver2}.so
%{_libdir}/libwx_%{buildname}_xrc-%{ver2}.so
%if 0%{?fedora} || 0%{?suse_version}
%{_libdir}/libwx_%{buildname}_webview-%{ver2}.so
%endif
# static libs
%{_libdir}/libwx_%{buildname}_adv-%{ver2}.a
%{_libdir}/libwx_%{buildname}_aui-%{ver2}.a
%{_libdir}/libwx_%{buildname}_core-%{ver2}.a
%{_libdir}/libwx_%{buildname}_gl-%{ver2}.a
%{_libdir}/libwx_%{buildname}_html-%{ver2}.a
#%{_libdir}/libwx_%{buildname}_media-%{ver2}.a
%{_libdir}/libwx_%{buildname}_propgrid-%{ver2}.a
%{_libdir}/libwx_%{buildname}_qa-%{ver2}.a
%{_libdir}/libwx_%{buildname}_ribbon-%{ver2}.a
%{_libdir}/libwx_%{buildname}_richtext-%{ver2}.a
%{_libdir}/libwx_%{buildname}_stc-%{ver2}.a
%{_libdir}/libwx_%{buildname}_xrc-%{ver2}.a
%if 0%{?fedora} || 0%{?suse_version}
%{_libdir}/libwx_%{buildname}_webview-%{ver2}.a
%endif
%dir %{_libdir}/wx
%{_libdir}/wx/config/%{wxconfig}
%{_libdir}/wx/include/%{wxconfig}/wx/setup.h
%{_libdir}/wx/config/%{wxconfigstatic}
%{_libdir}/wx/include/%{wxconfigstatic}/wx/setup.h
%{_bindir}/wx*
%{_datadir}/doc

%files -n %{wxbasename}
%{_libdir}/libwx_base*-%{ver2}.so.*

%files -n %{wxbasename}-devel -f wxbase-headers.paths
%dir %{_includedir}/wx-%{ver2}
%{_libdir}/libwx_base*-%{ver2}.so
%{_libdir}/libwx_base*-%{ver2}.a
%if %{unicode}
    %{_libdir}/libwxregexu-%{ver2}.a
%endif
%{_libdir}/libwxexpat-%{ver2}.a
%{_libdir}/libwxzlib-%{ver2}.a
%{_libdir}/libwxscintilla-%{ver2}.a
%dir %{_libdir}/wx
%{_datadir}/aclocal/*.m4
%{_datadir}/bakefile/presets/*

%files gl
%defattr(-,root,root)
%{_libdir}/libwx_%{buildname}_gl-%{ver2}.so.*

#%changelog

