Name:       libkdegames
Version:    15.04.0
Release:    1
Summary:    Common code and data for many KDE games
License:    GPLv2
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
BuildRequires:  kf5-kcodecs-dev
BuildRequires:  kf5-karchive-dev
BuildRequires:  kf5-kdbusaddons-dev
BuildRequires:  kf5-kdnssd-dev
BuildRequires:  kf5-kdeclarative-dev
BuildRequires:  kf5-ki18n-dev
BuildRequires:  kf5-kguiaddons-dev
BuildRequires:  kf5-kservice-dev
BuildRequires:  kf5-kconfigwidgets-dev
BuildRequires:  kf5-kitemviews-dev
BuildRequires:  kf5-kiconthemes-dev
BuildRequires:  kf5-kcompletion-dev
BuildRequires:  kf5-kjobwidgets-dev
BuildRequires:  kf5-ktextwidgets-dev
BuildRequires:  kf5-kglobalaccel-dev
BuildRequires:  kf5-kxmlgui-dev
BuildRequires:  kf5-kcrash-dev
BuildRequires:  kf5-kbookmarks-dev
BuildRequires:  kf5-kio-dev
BuildRequires:  kf5-knewstuff-dev
BuildRequires:  kf5-kdelibs4support-dev

%description
%{summary}.


%package dev
Summary:    Development files for %{name}
Requires:   %{name}%{?_isa} = %{version}-%{release}
%description dev
%{summary}.

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


%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%doc COPYING
%{_kf5_libdir}/libKF5KDEGames.so.*
%{_kf5_libdir}/libKF5KDEGamesPrivate.so.*
%{_kf5_qmldir}/org/kde/games
%{_kf5_datadir}/carddecks
%{_kf5_datadir}/kconf_update/*.upd


%files dev
%{_kf5_libdir}/cmake/KF5KDEGames
%{_kf5_includedir}/KF5KDEGames
%{_kf5_libdir}/libKF5KDEGames.so
%{_kf5_libdir}/libKF5KDEGamesPrivate.so


%changelog
* Mon May 04 2015 Daniel Vrátil <dvratil@redhat.com> - 15.04.0-1
- Initial version
