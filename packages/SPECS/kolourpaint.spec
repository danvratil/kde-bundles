%global     git_commit fc5706e
%global     git_date 20150505

Name:       kolourpaint
Version:    15.04.0
Release:    1
Summary:    KolourPaint is an easy-to-use paint program
License:    LGPLv2+ and GPLv2+
URL:        https://projects.kde.org/projects/kde/kdegraphics/%{name}

#%global revision %(echo %{version} | cut -d. -f3)
#%if %{revision} >= 50
#%global stable unstable
#%else
#%global stable stable
#%endif
#Source0: http://download.kde.org/%{stable}/applications/%{version}/src/%{name}-%{version}.tar.xz

Source0:        %{name}-%{git_commit}.tar.gz

BuildRequires:  extra-cmake-modules
BuildRequires:  kf5-rpm-macros
BuildRequires:  qt5-qtbase-dev

BuildRequires:  kf5-kdelibs4support-dev

BuildRequires:  desktop-file-utils

%description
%{summary}.

%prep
%setup -q -n %{name}-%{version}

%build
sed -i "s/\${GENERIC_LIB_VERSION}/5/"  CMakeLists.txt
sed -i "s/\${GENERIC_LIB_SOVERSION}/5\.0\.0/" CMakeLists.txt

mkdir %{_target_platform}
pushd %{_target_platform}
%{cmake_kf5} ..
popd

make %{?_smp_mflags} -C %{_target_platform}


%install
make install/fast DESTDIR=%{buildroot} -C %{_target_platform}
rm %{buildroot}%{_kf5_libdir}/libkolourpaint_lgpl.so

# Fix for exports
for s in %{buildroot}/%{_kf5_datadir}/icons/hicolor/*; do
    mv $s/apps/{%{name},org.kde.%{name}}.*
done
mv %{buildroot}/%{_kf5_datadir}/applications/{%{name},org.kde.%{name}}.desktop
sed -i "s/Icon=%{name}/Icon=org.kde.%{name}/" %{buildroot}/%{_kf5_datadir}/applications/org.kde.%{name}.desktop


%check
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
%{_kf5_bindir}/%{name}
%{_kf5_libdir}/libkolourpaint_lgpl.so.*
%{_kf5_datadir}/%{name}
%{_datadir}/applications/org.kde.%{name}.desktop
%{_datadir}/appdata/%{name}.appdata.xml
%{_kf5_datadir}/kxmlgui5/%{name}
%{_datadir}/doc/HTML/*/%{name}
%{_datadir}/icons/hicolor/*/*/*

%changelog
* Mon May 04 2015 Daniel Vrátil <dvratil@redhat.com> - 15.04.0-1
- Initial version
