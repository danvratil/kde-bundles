Name:           konversation
Summary:        KDE IRC client
Version:        1.6
Release:        1%{?dist}

License:        GPLv2+
URL:            https://projects.kde.org/projects/kde/kdenetwork/%{name}

Source0:        http://download.kde.org/stable/%{name}/%{version}/src/%{name}-%{version}.tar.xz

## upstreamable patches

BuildRequires:  desktop-file-utils

BuildRequires:  extra-cmake-modules
BuildRequires:  kf5-rpm-macros
BuildRequires:  qt5-qtbase-dev

BuildRequires:  kf5-karchive-dev
BuildRequires:  kf5-kbookmarks-dev
BuildRequires:  kf5-kconfig-dev
BuildRequires:  kf5-kconfigwidgets-dev
BuildRequires:  kf5-kdoctools-dev
BuildRequires:  kf5-kemoticons-dev
BuildRequires:  kf5-ki18n-dev
BuildRequires:  kf5-kidletime-dev
BuildRequires:  kf5-knotifyconfig-dev
BuildRequires:  kf5-kio-dev
BuildRequires:  kf5-kparts-dev
BuildRequires:  kf5-solid-dev
BuildRequires:  kf5-sonnet-dev
BuildRequires:  kf5-kwallet-dev
BuildRequires:  kf5-kwidgetsaddons-dev
BuildRequires:  kf5-kglobalaccel-dev
BuildRequires:  kf5-kdbusaddons-dev
BuildRequires:  kf5-knotifications-dev
BuildRequires:  kf5-kwindowsystem-dev
BuildRequires:  kf5-kiconthemes-dev
BuildRequires:  kf5-kitemviews-dev

BuildRequires:  phonon-dev

# TODO
#BuildRequires:  qca-dev


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
%find_lang konversation --with-qt

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

%files -f konversation.lang
%doc COPYING
%{_kf5_bindir}/%{name}*
%{_kf5_datadir}/%{name}
%{_kf5_datadir}/kconf_update/*
%{_kf5_datadir}/kxmlgui5/%{name}
%{_kf5_datadir}/knotifications5/%{name}.notifyrc
%{_kf5_datadir}/kservices5/*.protocol
%{_datadir}/applications/org.kde.%{name}.desktop
%{_datadir}/icons/hicolor/*/*/*
%{_docdir}/HTML/*/%{name}


%changelog
* Tue May 05 2015 Daniel Vrátil <dvratil@redhat.com> - 1.6-1
- Initial version (forked from Fedora)
