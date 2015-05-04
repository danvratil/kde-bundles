Name:       trojita
Version:    0.5
Release:    1
Summary:    A fast and lightweight IMAP e-mail client designed with standard-compliance in mind
License:    GPL3+
URL:        http://trojita.flaska.net/


Source0:    http://sourceforge.net/projects/trojita/files/src/trojita-0.5.tar.bz2

BuildRequires:  extra-cmake-modules
BuildRequires:  qt5-qtbase-dev
BuildRequires:  qt5-qtsvg-dev
BuildRequires:  qt5-qtwebkit-dev
BuildRequires:  qt5-qttools-static

BuildRequires:  desktop-file-utils

%description
%{summary}.


%prep
%setup -q -n %{name}-%{version}

%build
mkdir %{_target_platform}
pushd %{_target_platform}
%{cmake} .. -DWITH_QT5=TRUE
popd

make %{?_smp_mflags} -C %{_target_platform}


%install
make install/fast DESTDIR=%{buildroot} -C %{_target_platform}


%check
appstream-util validate-relax --nonet %{buildroot}%{_datadir}/appdata/%{name}.appdata.xml ||:
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop

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
%doc LICENSE
%{_bindir}/trojita
%{_bindir}/be.contacts
%{_libdir}/libtrojita_plugins.so
%{_datadir}/appdata/trojita.appdata.xml
%{_datadir}/applications/trojita.desktop
%{_datadir}/icons/hicolor/*/*/*
%{_datadir}/trojita

%changelog
* Mon May 04 2015 Daniel Vrátil <dvratil@redhat.com> - 0.5-1
- Initial version
