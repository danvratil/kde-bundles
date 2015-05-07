Name:           gwenview
Summary:        KDE image viewer
Version:        15.04.0
Release:        1%{?dist}

# app: GPLv2+
# lib:  IJG and (LGPLv2 or LGPLv3 or LGPLv3+ (KDE e.V.)) and LGPLv2+ and GPLv2+
License:        GPLv2+
URL:            https://projects.kde.org/projects/kde/kdegraphics/%{name}

%global revision %(echo %{version} | cut -d. -f3)
%if %{revision} >= 50
%global stable unstable
%else
%global stable stable
%endif
Source0:        http://download.kde.org/%{stable}/applications/%{version}/src/%{name}-%{version}.tar.xz

## upstreamable patches

BuildRequires: cmake
BuildRequires: desktop-file-utils
BuildRequires: extra-cmake-modules
BuildRequires: gettext
BuildRequires: kf5-rpm-macros
BuildRequires: kf5-kactivities-dev
BuildRequires: kf5-kdelibs4support-dev
BuildRequires: kf5-kio-dev
## frameworks soon to come (hopefully) -- rex
BuildRequires: libkdcraw-dev
#BuildRequires: kf5-kipi-dev
#BuildRequires: libappstream-glib
BuildRequires: libjpeg-dev
BuildRequires: pkgconfig(exiv2)
#BuildRequires: pkgconfig(lcms2)
#BuildRequires: pkgconfig(libpng)
BuildRequires: pkgconfig(phonon4qt5)
BuildRequires: pkgconfig(Qt5DBus) pkgconfig(Qt5Widgets) pkgconfig(Qt5Script) pkgconfig(Qt5Test)
BuildRequires: pkgconfig(Qt5Concurrent) pkgconfig(Qt5Svg) pkgconfig(Qt5OpenGL)
BuildRequires: pkgconfig(Qt5X11Extras)


%description
%{summary}.


%prep
%setup -q


%build
mkdir %{_target_platform}
pushd %{_target_platform}
%{cmake_kf5} ..
popd

make %{?_smp_mflags} -C %{_target_platform}


%install
make install/fast DESTDIR=%{buildroot} -C %{_target_platform}

# Fix for exports
for s in %{buildroot}/%{_kf5_datadir}/icons/hicolor/*; do
    mv $s/apps/{%{name},org.kde.%{name}}.*
done
sed -i "s/Icon=%{name}/Icon=org.kde.%{name}/" %{buildroot}/%{_kf5_datadir}/applications/org.kde.%{name}.desktop


%check
appstream-util validate-relax --nonet %{buildroot}%{_kf5_datadir}/appdata/%{name}.appdata.xml ||:
desktop-file-validate %{buildroot}%{_datadir}/applications/org.kde.%{name}.desktop


%post
/sbin/ldconfig
touch --no-create %{_kf5_datadir}/icons/hicolor &> /dev/null || :

%postun
/sbin/ldconfig
if [ $1 -eq 0 ] ; then
touch --no-create %{_kf5_datadir}/icons/hicolor &> /dev/null
gtk-update-icon-cache %{_kf5_datadir}/icons/hicolor &> /dev/null || :
fi

%posttrans
gtk-update-icon-cache %{_kf5_datadir}/icons/hicolor &> /dev/null || :

%files
%doc COPYING
%{_kf5_bindir}/%{name}*
%{_datadir}/applications/org.kde.%{name}.desktop
%{_datadir}/appdata/%{name}.appdata.xml
%{_datadir}/icons/hicolor/*/*/*
%{_docdir}/HTML/en/%{name}/
%{_kf5_datadir}/gvpart/
%{_kf5_datadir}/kxmlgui5/%{name}/
%{_kf5_datadir}/kservices5/gvpart.desktop
%{_kf5_datadir}/%{name}/
%{_kf5_datadir}/kservices5/ServiceMenus/slideshow.desktop
%{_kf5_libdir}/libgwenviewlib.so.*
%{_kf5_qtplugindir}/gvpart.so


%changelog
* Wed Apr 29 2015 Daniel Vrátil <dvratil@redhat.com> - 15.04.0-1
- Initial version (forked from Fedora)
