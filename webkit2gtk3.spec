%global __provides_exclude_from ^%{_libdir}/webkit2gtk-4\\.0/.*\\.so$
%global _dwz_max_die_limit 250000000
%global _dwz_max_die_limit_x86_64 250000000
#build gtkdoc failed on x86_64
%ifarch aarch64
%bcond_without docs
%endif


#Basic Information
Name:           webkit2gtk3
Version:        2.32.4
Release:        2
Summary:        GTK+ Web content engine library
License:        LGPLv2
URL:            http://www.webkitgtk.org/
Source0:        http://webkitgtk.org/releases/webkitgtk-%{version}.tar.xz
Source1:        https://webkitgtk.org/releases/webkitgtk-%{version}.tar.xz.asc

Patch6000:	backport-CVE-2021-42762.patch

#Dependency
BuildRequires:  at-spi2-core-devel bison cairo-devel cmake enchant2-devel
BuildRequires:  flex fontconfig-devel freetype-devel ninja-build
BuildRequires:  git geoclue2-devel gettext gcc-c++ glib2-devel gnutls-devel
BuildRequires:  gobject-introspection-devel gperf gnupg2 wpebackend-fdo-devel
BuildRequires:  gstreamer1-devel gstreamer1-plugins-base-devel rubygem-json
BuildRequires:  gstreamer1-plugins-bad-free-devel libwpe-devel libseccomp-devel
BuildRequires:  gtk3-devel gtk-doc geoclue2-devel libjpeg-turbo-devel
BuildRequires:  harfbuzz-devel hyphen-devel bubblewrap xdg-dbus-proxy
BuildRequires:  libatomic libicu-devel libjpeg-devel libnotify-devel
BuildRequires:  libpng-devel libsecret-devel libsoup-devel libwebp-devel
BuildRequires:  libxslt-devel libXt-devel libwayland-client-devel
BuildRequires:  libwayland-egl-devel libwayland-server-devel openjpeg2-devel
BuildRequires:  mesa-libEGL-devel mesa-libGL-devel libglvnd-devel
BuildRequires:  pcre-devel perl-File-Copy-Recursive perl-JSON-PP perl-Switch
BuildRequires:  python3 ruby rubygems sqlite-devel upower-devel woff2-devel pkgconfig(libsystemd)
Requires:       geoclue2 bubblewrap xdg-dbus-proxy
Requires:       webkit2gtk3-jsc = %{version}-%{release}
Recommends:     xdg-desktop-portal-gtk

Provides:       bundled(angle)
Provides:       bundled(xdgmime)

Obsoletes:      libwebkit2gtk < 2.5.0
Provides:       libwebkit2gtk = %{version}-%{release}
Obsoletes:      webkitgtk4 < %{version}-%{release}
Provides:       webkitgtk4 = %{version}-%{release}
Obsoletes:      webkit2gtk3-plugin-process-gtk2 < %{version}-%{release}
Provides:       webkit2gtk3-plugin-process-gtk2 = %{version}-%{release}
Obsoletes:      webkitgtk4-plugin-process-gtk2 < %{version}-%{release}
Provides:       webkitgtk4-plugin-process-gtk2 = %{version}-%{release}

%description
WebKitGTK is a full-featured port of the WebKit rendering engine,
suitable for projects requiring any kind of web integration, from
hybrid HTML/CSS applications to full-fledged web browsers. This
package contains WebKit2 based WebKitGTK+ for GTK+ 3.

%package        devel
Summary:        Development files for webkit2gtk3
Requires:       %{name} = %{version}-%{release}
Requires:       %{name}-jsc = %{version}-%{release}
Requires:       %{name}-jsc-devel = %{version}-%{release}
Obsoletes:      webkitgtk4-devel < %{version}-%{release}
Provides:       webkitgtk4-devel = %{version}-%{release}

%description    devel
The webkit2gtk3-devel package contains libraries, build data, and header
files for developing applications that use webkit2gtk3.

%if %{with docs}
%package        help
Summary:        Documentation files for webkit2gtk3
BuildArch:      noarch
Requires:       %{name} = %{version}-%{release}
Obsoletes:      %{name}-doc < %{version}-%{release}
Provides:       %{name}-doc = %{version}-%{release}
Obsoletes:      webkitgtk4-doc < %{version}-%{release}
Provides:       webkitgtk4-doc = %{version}-%{release}

%description    help
This package contains developer documentation for webkit2gtk3.
%endif

%package        jsc
Summary:        JavaScript engine from webkit2gtk3
Obsoletes:      webkitgtk4-jsc < %{version}-%{release}
Provides:       webkitgtk4-jsc = %{version}-%{release}

%description    jsc
This package contains JavaScript engine from webkit2gtk3.

%package        jsc-devel
Summary:        Development files for JavaScript engine from webkit2gtk3
Requires:       %{name}-jsc = %{version}-%{release}
Obsoletes:      webkitgtk4-jsc-devel < %{version}-%{release}
Provides:       webkitgtk4-jsc-devel = %{version}-%{release}

%description    jsc-devel
The webkit2gtk3-jsc-devel package contains libraries, build data, and header
files for developing applications that use JavaScript engine from webkit2gtk3.

#Build sections
%prep
%autosetup -p1 -n webkitgtk-%{version}

# rm bundled libraries
rm -rf Source/ThirdParty/gtest/
rm -rf Source/ThirdParty/qunit/

%build
%global optflags %(echo %{optflags} -Wl,--no-keep-memory | sed 's/-g /-g1 /')
mkdir -p %{_target_platform}
pushd %{_target_platform}
%cmake \
  -GNinja \
  -DPORT=GTK \
  -DCMAKE_BUILD_TYPE=Release \
%if %{with docs}
  -DENABLE_GTKDOC=ON \
%endif
  -DENABLE_MINIBROWSER=ON \
  -DPYTHON_EXECUTABLE=%{_bindir}/python3 \
  -DENABLE_GAMEPAD=OFF \
  -DCMAKE_EXE_LINKER_FLAGS="-Wl,--as-needed -Wl,-z,now -pthread" \
  -DCMAKE_MODULE_LINKER_FLAGS="-Wl,--as-needed -Wl,-z,now -pthread" \
  -DCMAKE_SHARED_LINKER_FLAGS="-Wl,--as-needed -Wl,-z,now -pthread" \
%ifarch aarch64
  -DENABLE_JIT=OFF \
  -DUSE_SYSTEM_MALLOC=ON \
%endif
%if 0%{?openEuler}
%ifarch aarch64
  -DUSE_64KB_PAGE_BLOCK=ON \
%endif
%endif
  ..
popd

export NINJA_STATUS="[%f/%t][%e] "
%ninja_build -C %{_target_platform}

%install
%ninja_install -C %{_target_platform}

%find_lang WebKit2GTK-4.0

#Files list
# Finally, copy over and rename various files for %%license inclusion
mkdir -p temp_copyrights
for f in $(find Source -regex ".*\(LICENSE\|COPYING\).*" | grep -v test);do
    cp -a $f temp_copyrights/${f//\//.}
done

%files -f WebKit2GTK-4.0.lang
%license temp_copyrights/*ThirdParty*
%license temp_copyrights/*WebCore*
%license temp_copyrights/*WebInspectorUI*
%license temp_copyrights/*WTF*
%{_libdir}/libwebkit2gtk-4.0.so.*
%dir %{_libdir}/girepository-1.0
%{_libdir}/girepository-1.0/WebKit2-4.0.typelib
%{_libdir}/girepository-1.0/WebKit2WebExtension-4.0.typelib
%{_libdir}/webkit2gtk-4.0/
%{_libexecdir}/webkit2gtk-4.0/
%exclude %{_libexecdir}/webkit2gtk-4.0/MiniBrowser
%{_bindir}/WebKitWebDriver

%files devel
%{_libexecdir}/webkit2gtk-4.0/MiniBrowser
%{_includedir}/webkitgtk-4.0/
%exclude %{_includedir}/webkitgtk-4.0/JavaScriptCore
%{_libdir}/libwebkit2gtk-4.0.so
%{_libdir}/pkgconfig/webkit2gtk-4.0.pc
%{_libdir}/pkgconfig/webkit2gtk-web-extension-4.0.pc
%dir %{_datadir}/gir-1.0
%{_datadir}/gir-1.0/WebKit2-4.0.gir
%{_datadir}/gir-1.0/WebKit2WebExtension-4.0.gir

%files jsc
%license temp_copyrights/*JavaScriptCore*
%{_libdir}/libjavascriptcoregtk-4.0.so.*
%dir %{_libdir}/girepository-1.0
%{_libdir}/girepository-1.0/JavaScriptCore-4.0.typelib

%files jsc-devel
%{_libexecdir}/webkit2gtk-4.0/jsc
%dir %{_includedir}/webkitgtk-4.0
%{_includedir}/webkitgtk-4.0/JavaScriptCore/
%{_libdir}/libjavascriptcoregtk-4.0.so
%{_libdir}/pkgconfig/javascriptcoregtk-4.0.pc
%dir %{_datadir}/gir-1.0
%{_datadir}/gir-1.0/JavaScriptCore-4.0.gir

%if %{with docs}
%files help
%dir %{_datadir}/gtk-doc
%dir %{_datadir}/gtk-doc/html
%{_datadir}/gtk-doc/html/jsc-glib-4.0/
%{_datadir}/gtk-doc/html/webkit2gtk-4.0/
%{_datadir}/gtk-doc/html/webkitdomgtk-4.0/
%endif

%changelog
* Thu Nov 04 2021 liuyumeng<liuyumeng5@huawei.com> - 2.32.4-2
- fix CVE-2021-42762

* Fri Oct 22 2021 zhanzhimin<zhanzhimin@huawei.com> - 2.32.4-1
- upgrade to 2.32.4

* Thu Jul 29 2021 wangkerong<wangkerong@huawei.com> - 2.32.1-2
- change xdg-desktop-protal-gts dependences

* Mon Jun 21 2021 wangkerong<wangkerong@huawei.com> - 2.32.1-1
- upgrade to 2.32.1

* Tue Dec 15 2020 hanhui<hanhui15@huawei.com> - 2.28.3-3
- modify license

* Wed Aug 05 2020 songnannan <songnannan2@huawei.com> - 2.28.3-2
- change the mesa-libELGS-devel to libglvnd-devel

* Thu Jul 23 2020 songnannan <songnannan2@huawei.com> - 2.28.3-1
- Type:enhancement
- Id:NA
- SUG:NA
- DESC: update to  2.28.3

* Mon Feb 24 2020 openEuler Buildteam <buildteam@openeuler.org> - 2.22.2-6
- Type:enhancement
- Id:NA
- SUG:NA
- DESC:fix rpmbuild fail in make

* Thu Jan 23 2020 openEuler Buildteam <buildteam@openeuler.org> - 2.22.2-5
- Type:enhancement
- Id:NA
- SUG:NA
- DESC:close build option gtkdoc

* Sat Jan 11 2020 openEuler Buildteam <buildteam@openeuler.org> - 2.22.2-4
- Type:enhancement
- Id:NA
- SUG:NA
- DESC:optimization the spec

* Tue Dec 31 2019 openEuler Buildteam <buildteam@openeuler.org> - 2.22.2-3
- Enable gtk-doc and go-introspection

* Fri Nov 8 2019 openEuler Buildteam <buildteam@openeuler.org> - 2.22.2-2
- Modify cmake option to disable gtk-doc and go-introspection

* Wed Sep 18 2019 openEuler Buildteam <buildteam@openeuler.org> - 2.22.2-1
- Package init

