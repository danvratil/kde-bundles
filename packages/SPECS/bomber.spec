Name:       bomber
Version:    15.04.0
Release:    1
Summary:    Bomber is a single player arcade game
License:    LGPLv2+ and GPLv2+
URL:        https://projects.kde.org/projects/kdegames/bomber

%global revision %(echo %{version} | cut -d. -f3)
%if %{revision} >= 50
%global stable unstable
%else
%global stable stable
%endif
Source0: http://download.kde.org/%{stable}/applications/%{version}/src/%{name}-%{version}.tar.xz

BuildRequires:  extra-cmake-modules
BuildRequires:  kf5-rpm-macros
BuildRequires:  qt5-qtbase-dev

BuildRequires:  kf5-kcoreaddons-dev
BuildRequires:  kf5-kconfig-dev
BuildRequires:  kf5-kdbusaddons-dev
BuildRequires:  kf5-ki18n-dev
BuildRequires:  kf5-kconfigwidgets-dev
BuildRequires:  kf5-kxmlgui-dev
BuildRequires:  kf5-kio-dev

BuildRequires:  libkdegames-dev

BuildRequires:  phonon-dev

BuildRequires:  desktop-file-utils

%description
Marble is a Virtual Globe and World Atlas that you can use to learn more
about Earth: You can pan and zoom around and you can look up places and
roads. A mouse click on a place label will provide the respective
Wikipedia article.


%prep
%setup -q -n %{name}-%{version}

%build
mkdir %{_target_platform}
pushd %{_target_platform}
%{cmake_kf5} ..
popd

make %{?_smp_mflags} -C %{_target_platform}


%install
make install/fast DESTDIR=%{buildroot} -C %{_target_platform}


%check
appstream-util validate-relax --nonet %{buildroot}%{_datadir}/appdata/%{name}.appdata.xml ||:
desktop-file-validate %{buildroot}%{_datadir}/applications/org.kde.%{name}.desktop

%post
touch --no-create %{_kf5_datadir}/icons/hicolor &> /dev/null || :

%postun
if [ $1 -eq 0 ] ; then
touch --no-create %{_kf5_datadir}/icons/hicolor &> /dev/null
gtk-update-icon-cache %{_kf5_datadir}/icons/hicolor &> /dev/null || :
fi

%posttrans
touch --no-create %{_kf5_datadir}/icons/hicolor &> /dev/null || :

%files
%doc COPYING COPYING.LIB
%{_kf5_bindir}/bomber
%{_kf5_datadir}/bomber
%{_datadir}/icons/hicolor/*/*/*
%{_datadir}/appdata/bomber.appdata.xml
%{_datadir}/applications/org.kde.bomber.desktop
%{_datadir}/config.kcfg/bomber.kcfg
%{_datadir}/doc/HTML/*/bomber
%{_kf5_datadir}/kxmlgui5/bomber

%changelog
* Mon May 04 2015 Daniel Vrátil <dvratil@redhat.com> - 15.04.0-1
- Initial version
