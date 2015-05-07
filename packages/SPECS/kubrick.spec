%global     git_commit bb8c958

Name:       kubrick
Version:    15.04.0
Release:    1
Summary:    Kubrick is based on the famous Rubik's Cube
License:    GPLv2+
URL:        https://projects.kde.org/projects/kdegames/%{name}

#%global revision %(echo %{version} | cut -d. -f3)
#%if %{revision} >= 50
#%global stable unstable
#%else
#%global stable stable
#%endif
#Source0: http://download.kde.org/%{stable}/applications/%{version}/src/%{name}-%{version}.tar.xz

Source0:  %{name}-%{git_commit}.tar.gz

BuildRequires:  extra-cmake-modules
BuildRequires:  kf5-rpm-macros
BuildRequires:  qt5-qtbase-dev
BuildRequires:  qt5-qtsvg-dev


BuildRequires:  kf5-kcoreaddons-dev
BuildRequires:  kf5-kconfig-dev
BuildRequires:  kf5-kitemmodels-dev
BuildRequires:  kf5-kwidgetsaddons-dev
BuildRequires:  kf5-kconfig-dev
BuildRequires:  kf5-kdbusaddons-dev
BuildRequires:  kf5-ki18n-dev
BuildRequires:  kf5-kconfigwidgets-dev
BuildRequires:  kf5-kxmlgui-dev
BuildRequires:  kf5-kio-dev
BuildRequires:  kf5-knotifyconfig-dev
BuildRequires:  kf5-kdelibs4support-dev

BuildRequires:  libkdegames-dev

BuildRequires:  desktop-file-utils

BuildRequires:  pkgconfig(gl)

%description
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

# Fix for exports
for s in %{buildroot}/%{_kf5_datadir}/icons/hicolor/*; do
    mv $s/apps/{%{name},org.kde.%{name}}.*
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
