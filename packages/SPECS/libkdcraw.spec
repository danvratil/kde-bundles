%global git_date    20150505
%global git_commit  9850efb

Name:           libkdcraw
Summary:        A thread-safe wrapper around libraw
Version:        5.0.0
Release:        1.%{git_date}git%{git_commit}%{?dist}

# # KDE e.V. may determine that future LGPL versions are accepted
License:        GPLv2+ and LGPLv2+
URL:            https://www.kde.org

#%global revision %(echo %{version} | cut -d. -f3)
#%if %{revision} >= 50
#%global stable unstable
#%else
#%global stable stable
#%endif
#Source0:        http://download.kde.org/%{stable}/plasma/%{plasma_version}/%{framework}-%{version}.tar.xz

# git archive --format=tar.gz --remote=git://anongit.kde.org/libkdcraw.git \
#             --prefix=libkdcraw-%{version}/ --output=libkdcraw-%{git_commit}.tar.gz \
#             frameworks
Source0:        libkdcraw-%{git_commit}.tar.gz

BuildRequires:  extra-cmake-modules
BuildRequires:  kf5-rpm-macros
BuildRequires:  qt5-qtbase-dev

BuildRequires:  kf5-ki18n-dev
BuildRequires:  kf5-kconfig-dev
BuildRequires:  kf5-kwidgetsaddons-dev
BuildRequires:  kf5-kio-dev

BuildRequires:  LibRaw-dev >= 0.16

%description
%{summary}.

%package dev
Summary:        Developer files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       kf5-ki18n-dev

%description dev
%{summary}.


%prep
%setup -q -n libkdcraw-%{version}


%build
mkdir -p %{_target_platform}
pushd %{_target_platform}
%{cmake_kf5} ..
popd

make %{?_smp_mflags} -C %{_target_platform}


%install
make install/fast DESTDIR=%{buildroot} -C %{_target_platform}

%post
/sbin/ldconfig
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

%postun
/sbin/ldconfig
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

%posttrans
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :


%files
%doc COPYING COPYING.LIB
%{_kf5_libdir}/libKF5KDcraw.so.*
%{_datadir}/icons/hicolor/*/*/*.png
%{_datadir}/libkdcraw

%files dev
%{_kf5_libdir}/libKF5KDcraw.so
%{_kf5_libdir}/cmake/KF5KDcraw
%{_kf5_includedir}/KDCRAW
%{_kf5_includedir}/libkdcraw_version.h

%changelog
* Tue May 05 2015 Daniel Vrátil <dvratil@redhat.com> - 5.0.0-1.20150505git9850efb
- Initial version