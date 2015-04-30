Name:           kcalc
Summary:        KDE Scientific Calculator
Version:        15.04.0
Release:        1%{?dist}

License:        GPLv2+
URL:            https://projects.kde.org/projects/kde/kdeutils/kcalc
%global revision %(echo %{version} | cut -d. -f3)
%if %{revision} >= 50
%global stable unstable
%else
%global stable stable
%endif
Source0: http://download.kde.org/%{stable}/applications/%{version}/src/%{name}-%{version}.tar.xz

## upstreamable patches
# fix arithmetic fault in mod, factorial
#Patch0: kcalc-4.9.90-misc.patch

BuildRequires:  cmake
BuildRequires:  desktop-file-utils
BuildRequires:  extra-cmake-modules
BuildRequires:  gmp-dev
BuildRequires:  kf5-rpm-macros
BuildRequires:  kf5-kcompletion-dev
BuildRequires:  kf5-kconfig-dev
BuildRequires:  kf5-kconfigwidgets-dev
BuildRequires:  kf5-kcoreaddons-dev
BuildRequires:  kf5-kdbusaddons-dev
BuildRequires:  kf5-kdeclarative-dev
BuildRequires:  kf5-kdoctools-dev
BuildRequires:  kf5-kguiaddons-dev
BuildRequires:  kf5-ki18n-dev
BuildRequires:  kf5-kiconthemes-dev
BuildRequires:  kf5-kinit-dev
BuildRequires:  kf5-kitemviews-dev
BuildRequires:  kf5-kio-dev
BuildRequires:  kf5-kjobwidgets-dev
BuildRequires:  kf5-knewstuff-dev
BuildRequires:  kf5-knotifications-dev
BuildRequires:  kf5-knotifyconfig-dev
BuildRequires:  kf5-knewstuff-dev
BuildRequires:  kf5-kservice-dev
BuildRequires:  kf5-kwindowsystem-dev
BuildRequires:  kf5-kwidgetsaddons-dev
BuildRequires:  kf5-kxmlgui-dev
BuildRequires:  pkgconfig(Qt5Widgets)
#BuildRequires: libappstream-glib


%description
KCalc is a calculator which offers many more mathematical
functions than meet the eye on a first glance.


%prep
%setup -q

#%patch0 -p1 -b .misc


%build
mkdir %{_target_platform}
pushd %{_target_platform}
%{cmake_kf5} ..
popd

make %{?_smp_mflags} -C %{_target_platform}


%install
make install/fast DESTDIR=%{buildroot} -C %{_target_platform}


%check
#appstream-util validate-relax --nonet %{buildroot}%{_kf5_datadir}/appdata/%{name}.appdata.xml ||:
desktop-file-validate %{buildroot}%{_kf5_datadir}/applications/org.kde.%{name}.desktop ||:


%files
%doc COPYING*
#doc README
%{_kf5_bindir}/%{name}
%{_kf5_libdir}/libkdeinit5_%{name}.so
#{_sysconfdir}/xdg/%{name}.knsrc
%{_kf5_datadir}/applications/org.kde.%{name}.desktop
#{_datadir}/appdata/%{name}.appdata.xml
#{_kf5_datadir}/icons/hicolor/*/apps/%{name}.*
%{_kf5_datadir}/%{name}/
%{_docdir}/HTML/en/%{name}/
%{_kf5_datadir}/kconf_update/%{name}*
%{_kf5_datadir}/kxmlgui5/%{name}/
#{_kf5_datadir}/sounds/%{name}/
%{_kf5_datadir}/config.kcfg/%{name}.kcfg


%changelog
* Wed Apr 29 2015 Daniel Vrátil <dvratil@redhat.com> - 15.04.0-1
- Initial version (forked from Fedora)
