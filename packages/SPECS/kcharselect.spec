Name:       kcharselect
Version:    15.04.0
Release:    1
Summary:    A tool to select special characters from all installed fonts and copy them into the clipboard.
License:    LGPLv2+ and GPLv2+
URL:        https://projects.kde.org/projects/applications/%{name}

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

BuildRequires:  kf5-kdoctools-dev
BuildRequires:  kf5-ki18n-dev
BuildRequires:  kf5-kwidgetsaddons-dev
BuildRequires:  kf5-kxmlgui-dev

BuildRequires:  desktop-file-utils

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

# Fix for export
mv %{buildroot}/%{_datadir}/applications/org.kde.{KCharSelect,kcharselect}.desktop


%check
desktop-file-validate %{buildroot}%{_datadir}/applications/org.kde.%{name}.desktop

%files
%doc COPYING COPYING.LIB
%{_kf5_bindir}/%{name}
%{_datadir}/applications/org.kde.%{name}.desktop
%{_kf5_datadir}/kxmlgui5/%{name}
%{_datadir}/doc/HTML/*/%{name}

%changelog
* Mon May 04 2015 Daniel Vrátil <dvratil@redhat.com> - 15.04.0-1
- Initial version
