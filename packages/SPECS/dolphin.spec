%define git_commit 9456584

Name:           dolphin
Summary:        KDE File Manager
Version:        15.04.0
Release:        1%{?dist}

# app: GPLv2+
# lib:  IJG and (LGPLv2 or LGPLv3 or LGPLv3+ (KDE e.V.)) and LGPLv2+ and GPLv2+
License:        GPLv2+
URL:            https://projects.kde.org/projects/kde/applications/dolphin
#%global revision %(echo %{version} | cut -d. -f3)
#%if %{revision} >= 50
#%global stable unstable
#%else
#%global stable stable
#%endif
#Source0:        http://download.kde.org/%{stable}/applications/%{version}/src/%{name}-%{version}.tar.xz
Source0:        dolphin-%{git_commit}.tar.gz

## upstreamable patches

BuildRequires:  cmake
BuildRequires:  desktop-file-utils
BuildRequires:  extra-cmake-modules
BuildRequires:  gettext
BuildRequires:  kf5-rpm-macros

BuildRequires:  qt5-qtbase-dev

BuildRequires:  kf5-kdoctools-dev
BuildRequires:  kf5-kinit-dev
BuildRequires:  kf5-kcmutils-dev
BuildRequires:  kf5-knewstuff-dev
BuildRequires:  kf5-kcoreaddons-dev
BuildRequires:  kf5-ki18n-dev
BuildRequires:  kf5-kdbusaddons-dev
BuildRequires:  kf5-kbookmarks-dev
BuildRequires:  kf5-kconfig-dev
BuildRequires:  kf5-kio-dev
BuildRequires:  kf5-kparts-dev
BuildRequires:  kf5-solid-dev
BuildRequires:  kf5-kiconthemes-dev
BuildRequires:  kf5-kcompletion-dev
BuildRequires:  kf5-ktexteditor-dev
BuildRequires:  kf5-kwindowsystem-dev
BuildRequires:  kf5-knotifications-dev

BuildRequires:  kf5-kactivities-dev
BuildRequires:  phonon-dev


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


%check
appstream-util validate-relax --nonet %{buildroot}%{_kf5_datadir}/appdata/%{name}.appdata.xml ||:
desktop-file-validate %{buildroot}%{_kde4_datadir}/applications/org.kde.%{name}.desktop


%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%doc COPYING
%{_kf5_bindir}/%{name}
%{_kf5_datadir}/applications/org.kde.%{name}.desktop
%{_datadir}/appdata/%{name}.appdata.xml
%{_docdir}/HTML/en/dolphin/


%changelog
* Thu Apr 30 2015 Daniel Vrátil <dvratil@redhat.com> - 15.04.0-1
- Initial version (forked from Fedora)
