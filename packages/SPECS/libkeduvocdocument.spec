Name:           libkeduvocdocument
Summary:        Library to parse, convert, and manipulate KVTML files
Version:        15.04.0
Release:        1%{?dist}

# # KDE e.V. may determine that future LGPL versions are accepted
License:        GPLv2+ and LGPLv2+
URL:            https://www.kde.org

%global revision %(echo %{version} | cut -d. -f3)
%if %{revision} >= 50
%global stable unstable
%else
%global stable stable
%endif
Source0:        http://download.kde.org/%{stable}/applications/%{version}/src/%{name}-%{version}.tar.xz


BuildRequires:  extra-cmake-modules
BuildRequires:  kf5-rpm-macros
BuildRequires:  qt5-qtbase-dev
BuildRequires:  qt5-qtxmlpatterns-dev

BuildRequires:  kf5-ki18n-dev
BuildRequires:  kf5-karchive-dev
BuildRequires:  kf5-kio-dev

%description
%{summary}.

%package dev
Summary:        Developer files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description dev
%{summary}.


%prep
%setup -q -n %{name}-%{version}


%build
mkdir -p %{_target_platform}
pushd %{_target_platform}
%{cmake_kf5} ..
popd

make %{?_smp_mflags} -C %{_target_platform}


%install
make install/fast DESTDIR=%{buildroot} -C %{_target_platform}

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%doc COPYING COPYING.LIB
%{_kf5_libdir}/libKEduVocDocument.so.*

%files dev
%{_kf5_libdir}/libKEduVocDocument.so
%{_kf5_libdir}/cmake/libkeduvocdocument
%{_includedir}/libkeduvocdocument

%changelog
* Tue May 05 2015 Daniel Vrátil <dvratil@redhat.com> - 15.04.0-1
- Initial version