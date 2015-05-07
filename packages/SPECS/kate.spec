Name:       kate
Summary:    KDE Advanced Text Editor
Version:    15.04.0
Release:    1%{?dist}

# kwrite LGPLv2+
# kate: app LGPLv2, plugins, LGPLv2 and LGPLv2+ and GPLv2+
# ktexteditor: LGPLv2
License:    LGPLv2 and LGPLv2+ and GPLv2+
URL:        https://projects.kde.org/projects/kde/applications/kate

%global revision %(echo %{version} | cut -d. -f3)
%if %{revision} >= 50
%global stable unstable
%else
%global stable stable
%endif
Source0: http://download.kde.org/%{stable}/applications/%{version}/src/kate-%{version}.tar.xz

BuildRequires:  cmake
BuildRequires:  extra-cmake-modules
BuildRequires:  desktop-file-utils
BuildRequires:  gettext
#BuildRequires:  pkgconfig(libgit2)
BuildRequires:  pkgconfig(x11)
BuildRequires:  kf5-rpm-macros
BuildRequires:  kf5-kconfig-dev
BuildRequires:  kf5-kdoctools-dev
BuildRequires:  kf5-kguiaddons-dev
BuildRequires:  kf5-ki18n-dev
BuildRequires:  kf5-kinit-dev
BuildRequires:  kf5-kio-dev
BuildRequires:  kf5-kitemmodels-dev
BuildRequires:  kf5-kjobwidgets-dev
BuildRequires:  kf5-knewstuff-dev
BuildRequires:  kf5-knotifications-dev
BuildRequires:  kf5-kparts-dev
BuildRequires:  kf5-ktexteditor-dev
BuildRequires:  kf5-kwindowsystem-dev
BuildRequires:  kf5-kxmlgui-dev
BuildRequires:  kf5-kservice-dev
BuildRequires:  kf5-plasma-dev
BuildRequires:  kf5-threadweaver-dev
BuildRequires:  kf5-kwallet-dev

BuildRequires:  qt5-qtbase-dev


%description
%{summary}.


%prep
%setup -q -n %{name}-%{version}


%build
mkdir %{_target_platform}
pushd %{_target_platform}
%{cmake_kf5} \
     -DSYSCONF_INSTALL_DIR:PATH=%{_prefix}/%{_sysconfdir} \
     -DBUILD_kwrite:BOOL=OFF \
    ..
popd

make %{?_smp_mflags} -C %{_target_platform}


%install
make install/fast DESTDIR=%{buildroot} -C %{_target_platform}

# Fix for exports
for s in %{buildroot}/%{_kf5_datadir}/icons/hicolor/*; do
    mv $s/apps/{%{name},org.kde.%{name}}.*
done
sed -i "s/Icon=%{name}/Icon=%{name}/" %{buildroot}/%{_kf5_datadir}/applications/org.kde.%{name}.desktop


%check
desktop-file-validate %{buildroot}%{_kf5_datadir}/applications/org.kde.%{name}.desktop


%post
touch --no-create %{_kf5_datadir}/icons/hicolor &> /dev/null || :

%posttrans
gtk-update-icon-cache %{_kf5_datadir}/icons/hicolor &> /dev/null || :
update-desktop-database -q &> /dev/null || :

%postun
if [ $1 -eq 0 ] ; then
touch --no-create %{_kf5_datadir}/icons/hicolor &> /dev/null || :
gtk-update-icon-cache %{_kf5_datadir}/icons/hicolor &> /dev/null || :
update-desktop-database -q &> /dev/null || :
fi

%files
%license COPYING.LIB
%doc AUTHORS
%config(noreplace) %{_prefix}/%{_sysconfdir}/xdg/katerc
%{_kf5_bindir}/kate
%{_kf5_libdir}/libkdeinit5_kate.so
%{_kf5_datadir}/applications/org.kde.kate.desktop
%{_datadir}/appdata/org.kde.kate.appdata.xml
%{_kf5_datadir}/icons/hicolor/*/*
%{_mandir}/man1/kate.1*
%{_docdir}/HTML/*/*
%{_kf5_datadir}/kxmlgui5/kate
%{_kf5_datadir}/plasma/plasmoids/org.kde.plasma.katesessions/
%{_kf5_datadir}/kservices5/plasma-applet-org.kde.plasma.katesessions.desktop
%{_kf5_datadir}/kservices5/plasma-dataengine-katesessions.desktop
%{_kf5_datadir}/plasma/services/org.kde.plasma.katesessions.operations
# plugins
%config(noreplace) %{_prefix}/%{_sysconfdir}/xdg/ktexteditor_codesnippets_core.knsrc
%{_kf5_qtplugindir}/ktexteditor/katebacktracebrowserplugin.so
%{_kf5_qtplugindir}/ktexteditor/katebuildplugin.so
%{_kf5_qtplugindir}/ktexteditor/katecloseexceptplugin.so
%{_kf5_qtplugindir}/ktexteditor/katectagsplugin.so
%{_kf5_qtplugindir}/ktexteditor/katefilebrowserplugin.so
%{_kf5_qtplugindir}/ktexteditor/katefiletreeplugin.so
%{_kf5_qtplugindir}/ktexteditor/kategdbplugin.so
%{_kf5_qtplugindir}/ktexteditor/katekonsoleplugin.so
%{_kf5_qtplugindir}/ktexteditor/kateopenheaderplugin.so
%{_kf5_qtplugindir}/ktexteditor/kateprojectplugin.so
%{_kf5_qtplugindir}/ktexteditor/katesearchplugin.so
%{_kf5_qtplugindir}/ktexteditor/katesnippetsplugin.so
%{_kf5_qtplugindir}/ktexteditor/katesqlplugin.so
%{_kf5_qtplugindir}/ktexteditor/katesymbolviewerplugin.so
%{_kf5_qtplugindir}/ktexteditor/katexmltoolsplugin.so
%{_kf5_qtplugindir}/ktexteditor/tabswitcherplugin.so
%{_kf5_qtplugindir}/plasma/dataengine/plasma_engine_katesessions.so
%{_kf5_datadir}/kateproject/
%{_kf5_datadir}/katexmltools/
%{_kf5_datadir}/kservices5/katesymbolviewerplugin.desktop
%{_kf5_datadir}/kxmlgui5/katebuild/
%{_kf5_datadir}/kxmlgui5/katecloseexceptplugin/
%{_kf5_datadir}/kxmlgui5/katectags/
%{_kf5_datadir}/kxmlgui5/katefiletree/
%{_kf5_datadir}/kxmlgui5/kategdb/
%{_kf5_datadir}/kxmlgui5/katekonsole/
%{_kf5_datadir}/kxmlgui5/kateopenheaderplugin/
%{_kf5_datadir}/kxmlgui5/kateproject/
%{_kf5_datadir}/kxmlgui5/katesearch/
%{_kf5_datadir}/kxmlgui5/katesnippets/
%{_kf5_datadir}/kxmlgui5/katesql/
%{_kf5_datadir}/kxmlgui5/katesymbolviewer/
%{_kf5_datadir}/kxmlgui5/katexmltools/
%{_kf5_datadir}/kxmlgui5/tabswitcher/

%changelog
* Tue Apr 28 2015 Daniel Vrátil <dvratil@redhat.com> - 15.04.0-1
- Initial version (forked from Fedora)
