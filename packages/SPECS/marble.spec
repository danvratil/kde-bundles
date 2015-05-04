Name:       marble
Version:    15.04.0
Release:    1
Summary:    KDE Virtual Globe application
License:    LGPLv2+ nad GPL3
URL:        https://projects.kde.org/projects/kdeedu/marble

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
BuildRequires:  qt5-qtsvg-dev
BuildRequires:  qt5-qtscript-dev
BuildRequires:  qt5-qtxmlpatterns-dev

BuildRequires:  desktop-file-utils

Requires:       %{name}-libs = %{version}-%{release}

%description
Marble is a Virtual Globe and World Atlas that you can use to learn more
about Earth: You can pan and zoom around and you can look up places and
roads. A mouse click on a place label will provide the respective
Wikipedia article.

%package libs
Summary:    Runtime libraries for %{name}
%description libs
%{summary}.

%package dev
Summary:    Development files for %{name}
Requires:   %{name}-libs%{?_isa} = %{version}-%{release}
%description dev
%{summary}.


%prep
%setup -q -n %{name}-%{version}

%build
mkdir %{_target_platform}
pushd %{_target_platform}
%{cmake_kf5} .. -DQT5BUILD=TRUE
popd

make %{?_smp_mflags} -C %{_target_platform}


%install
make install/fast DESTDIR=%{buildroot} -C %{_target_platform}


%check
appstream-util validate-relax --nonet %{buildroot}%{_kf5_datadir}/appdata/%{name}.appdata.xml ||:
desktop-file-validate %{buildroot}%{_kf5_datadir}/applications/marble_gpx.desktop
desktop-file-validate %{buildroot}%{_kf5_datadir}/applications/marble_osm.desktop
desktop-file-validate %{buildroot}%{_kf5_datadir}/applications/marble_kml.desktop


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
%doc COPYING.DOC LICENSE.txt LICENSE.GPL-3
%{_kf5_bindir}/marble-mobile
%{_kf5_bindir}/marble-qt
%{_kf5_bindir}/marble-touch
%dir %{_kf5_libdir}/marble/
%{_kf5_libdir}/marble/plugins/*
%{_kf5_libdir}/plugins/designer/*.so
%{_kf5_datadir}/marble
%{_kf5_datadir}/applications/*.desktop
%{_kf5_datadir}/icons/hicolor/*/*/marble.png
%{_kf5_datadir}/appdata/marble.appdata.xml

%post libs -p /sbin/ldconfig
%postun  libs -p /sbin/ldconfig

%files libs
%{_kf5_libdir}/libastro.so.*
%{_kf5_libdir}/libmarblewidget.so.*

%files dev
%{_includedir}/marble
%{_includedir}/astro
%{_kf5_libdir}/libastro.so
%{_kf5_libdir}/libmarblewidget.so

%changelog
* Mon May 04 2015 Daniel Vrátil <dvratil@redhat.com> - 15.04.0-1
- Initial version
