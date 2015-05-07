%global svn_date    20150505
%global svn_rev     1367987

Name:           qimageblitz
Summary:        An interm image effect library
Version:        5.0.0
Release:        1.%{svn_date}svn%{svn_rev}%{?dist}

License:        BSD
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
Source0:        %{name}-%{svn_rev}.tar.gz

BuildRequires:  extra-cmake-modules
BuildRequires:  kf5-rpm-macros
BuildRequires:  qt5-qtbase-dev

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

# Not installed
rm %{buildroot}%{_kf5_bindir}/blitztest

# Bad rpath is bad.
chrpath -d %{buildroot}/%{_kf5_libdir}/libqimageblitz.so.5.0.0

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%doc COPYING
%{_kf5_libdir}/libqimageblitz.so.*

%files dev
%{_kf5_libdir}/libqimageblitz.so
%{_includedir}/qimageblitz
%{_libdir}/pkgconfig/qimageblitz.pc

%changelog
* Tue May 05 2015 Daniel Vrátil <dvratil@redhat.com> - 5.0.0-1.20150505svn1367987
- Initial version