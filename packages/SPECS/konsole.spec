Name:       konsole
Summary:    KDE Terminal Emulator
Version:    15.04.0
Release:    1%{?dist}

# sources: MIT and LGPLv2 and LGPLv2+ and GPLv2+
License:    GPLv2 and GFDL
URL:        http://konsole.kde.org/
%global revision %(echo %{version} | cut -d. -f3)
%if %{revision} >= 50
%global stable unstable
%else
%global stable stable
%endif
Source0: http://download.kde.org/%{stable}/applications/%{version}/src/konsole-%{version}.tar.xz

#BuildRequires: cmake
BuildRequires:  extra-cmake-modules
BuildRequires:  gettext
BuildRequires:  pkgconfig(x11)
BuildRequires:  kf5-rpm-macros
BuildRequires:  kf5-kbookmarks-dev
BuildRequires:  kf5-kcompletion-dev
BuildRequires:  kf5-kcoreaddons-dev
BuildRequires:  kf5-kconfig-dev
BuildRequires:  kf5-kconfigwidgets-dev
BuildRequires:  kf5-kdoctools-dev
BuildRequires:  kf5-kguiaddons-dev
BuildRequires:  kf5-ki18n-dev
BuildRequires:  kf5-kiconthemes-dev
BuildRequires:  kf5-kinit-dev
BuildRequires:  kf5-kdelibs4support-dev
BuildRequires:  kf5-kio-dev
BuildRequires:  kf5-knotifications-dev
BuildRequires:  kf5-knotifyconfig-dev
BuildRequires:  kf5-kparts-dev
BuildRequires:  kf5-kpty-dev
BuildRequires:  kf5-kservice-dev
BuildRequires:  kf5-ktextwidgets-dev
BuildRequires:  kf5-kwidgetsaddons-dev
BuildRequires:  kf5-kwindowsystem-dev
BuildRequires:  kf5-kxmlgui-dev
## TODO?
#BuildRequires: kf5-konq-dev

BuildRequires:  qt5-qtbase-dev
BuildRequires:  qt5-qtscript-dev


Requires:       konsole-part = %{version}-%{release}

%description
%{summary}.


%package        part
Summary:        Konsole KPart plugin
%description    part
%{summary}.


%prep
%setup -q -n %{name}-%{version}


%build
mkdir %{_target_platform}
pushd %{_target_platform}
%{cmake_kf5} \
    ..
popd

make %{?_smp_mflags} -C %{_target_platform}


%install
make install/fast DESTDIR=%{buildroot} -C %{_target_platform}


%check
desktop-file-validate %{buildroot}%{_kf5_datadir}/applications/org.kde.konsole.desktop


%files
%doc README
%{_kf5_bindir}/konsole
%{_kf5_bindir}/konsoleprofile
%{_kf5_libdir}/libkdeinit5_konsole.so
%{_kf5_datadir}/applications/org.kde.konsole.desktop
%{_datadir}/appdata/org.kde.konsole.appdata.xml
%{_kf5_datadir}/knotifications5/konsole.notifyrc
%{_kf5_datadir}/kservices5/ServiceMenus/konsolehere.desktop
%{_kf5_datadir}/kservices5/ServiceMenus/konsolerun.desktop
%{_kf5_datadir}/kservicetypes5/terminalemulator.desktop
%{_kf5_datadir}/kxmlgui5/konsole/konsoleui.rc
%{_kf5_datadir}/kxmlgui5/konsole/sessionui.rc
%{_docdir}/HTML/en/konsole/

%post part -p /sbin/ldconfig
%postun part -p /sbin/ldconfig

%files part
%doc COPYING*
%{_kf5_datadir}/konsole/
%{_kf5_libdir}/libkonsoleprivate.so.15*
%{_kf5_qtplugindir}/konsolepart.so
%{_kf5_datadir}/kservices5/konsolepart.desktop
%{_kf5_datadir}/kxmlgui5/konsole/partui.rc

%changelog
* Tue Apr 28 2015 Daniel Vrátil <dvratil@redhat.com> - 15.04.0-1
- Initial version (forked from Fedora)
