#Global macro or variable
%global __provides_exclude_from ^%{_libdir}/webkit2gtk-4\\.0/.*\\.so$
# increase the DIE limit use linker flags to reduce memory consumption
# https://bugzilla.redhat.com/show_bug.cgi?id=1456261
%global _dwz_max_die_limit 250000000
%global _dwz_max_die_limit_x86_64 250000000
%global optflags %(echo %{optflags} | sed 's/-g /-g1 /')

#Basic Information
Name:           webkit2gtk3
Version:        2.22.2
Release:        9
Summary:        GTK+ Web content engine library
License:        LGPLv2 AND BSD-3-Clause AND ICU AND MIT
URL:            http://www.webkitgtk.org/
Source0:        http://webkitgtk.org/releases/webkitgtk-%{version}.tar.xz

# https://bugs.webkit.org/show_bug.cgi?id=162611
Patch0:     user-agent-branding.patch
# https://bugs.webkit.org/show_bug.cgi?id=132333
Patch2:     cloop-big-endians.patch
# Explicitly specify python2 over python
Patch3:     python2.patch
Patch4:     webkit-aarch64_page_size.patch

#Dependency
BuildRequires:  at-spi2-core-devel bison cairo-devel cmake enchant-devel
BuildRequires:  flex fontconfig-devel freetype-devel ninja-build
BuildRequires:  git geoclue2-devel gettext gcc-c++ glib2-devel gnutls-devel
BuildRequires:  gobject-introspection-devel gperf
BuildRequires:  gstreamer1-devel gstreamer1-plugins-base-devel
BuildRequires:  gstreamer1-plugins-bad-free-devel
BuildRequires:  gtk2-devel gtk3-devel gtk-doc
BuildRequires:  harfbuzz-devel hyphen-devel
BuildRequires:  libatomic libicu-devel libjpeg-devel libnotify-devel
BuildRequires:  libpng-devel libsecret-devel libsoup-devel libwebp-devel
BuildRequires:  libxslt-devel libXt-devel libwayland-client-devel
BuildRequires:  libwayland-egl-devel libwayland-server-devel
BuildRequires:  mesa-libEGL-devel mesa-libGL-devel libglvnd-devel
BuildRequires:  pcre-devel perl-File-Copy-Recursive perl-JSON-PP perl-Switch
BuildRequires:  python2 ruby rubygems sqlite-devel upower-devel woff2-devel
Requires:       geoclue2
Requires:       webkit2gtk3-jsc = %{version}-%{release}

Provides:       bundled(angle)

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
%autosetup -p1 -n webkitgtk-%{version} -S git

# rm bundled libraries
rm -rf Source/ThirdParty/gtest/
rm -rf Source/ThirdParty/qunit/

%build
mkdir -p %{_target_platform}
pushd %{_target_platform}
%cmake \
  -GNinja \
  -DPORT=GTK \
  -DCMAKE_BUILD_TYPE=Release \
  -DENABLE_GTKDOC=ON \
  -DENABLE_MINIBROWSER=ON \
%ifarch s390x %{power64} aarch64
  -DENABLE_JIT=OFF \
  -DUSE_SYSTEM_MALLOC=ON \
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

%files help
%dir %{_datadir}/gtk-doc
%dir %{_datadir}/gtk-doc/html
%{_datadir}/gtk-doc/html/jsc-glib-4.0/
%{_datadir}/gtk-doc/html/webkit2gtk-4.0/
%{_datadir}/gtk-doc/html/webkitdomgtk-4.0/

%changelog
* Tue Oct 13 2020 hanhui <hanhui15@huawei.com> - 2.22.2-9
- change mesa-libEGL-devel to libglvnd-devel in buildrequires

* Tue Aug 18 2020 smileknife<jackshan2010@aliyun.com> - 2.22.2-8
- update release for rebuilding

* Tue May 19 2020 openEuler Buildteam <buildteam@openeuler.org> - 2.22.2-7
- rebuild for libwebp

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

