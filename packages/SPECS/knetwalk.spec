Name:       knetwalk
Version:    15.04.0
Release:    1
Summary:    KNetWalk: connect all the terminals to the server, in as few turns as possible
License:    GPLv2+
URL:        https://projects.kde.org/projects/kdegames/%{name}

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
BuildRequires:  qt5-qtdeclarative-dev
BuildRequires:  qt5-qtsvg-dev

BuildRequires:  kf5-kcoreaddons-dev
BuildRequires:  kf5-kconfig-dev
BuildRequires:  kf5-kwidgetsaddons-dev
BuildRequires:  kf5-kdbusaddons-dev
BuildRequires:  kf5-ki18n-dev
BuildRequires:  kf5-kguiaddons-dev
BuildRequires:  kf5-kconfigwidgets-dev
BuildRequires:  kf5-kitemviews-dev
BuildRequires:  kf5-kiconthemes-dev
BuildRequires:  kf5-kxmlgui-dev
BuildRequires:  kf5-kio-dev
BuildRequires:  kf5-knotifyconfig-dev

BuildRequires:  libkdegames-dev

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

# Fix for exports
for s in %{buildroot}/%{_kf5_datadir}/icons/hicolor/*; do
    mv $s/actions/{%{name},org.kde.%{name}}.*
done
sed -i "s/Icon=%{name}/Icon=org.kde.%{name}/" %{buildroot}/%{_kf5_datadir}/applications/org.kde.%{name}.desktop


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
%doc COPYING COPYING.DOC
%{_kf5_bindir}/%{name}
%{_kf5_datadir}/%{name}
%{_datadir}/icons/hicolor/*/*/*
%{_datadir}/applications/org.kde.%{name}.desktop
%{_datadir}/doc/HTML/*/%{name}
%{_kf5_datadir}/kxmlgui5/%{name}

%changelog
* Mon May 04 2015 Daniel Vrátil <dvratil@redhat.com> - 15.04.0-1
- Initial version
