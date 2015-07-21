Name:       ksbinit
Version:    0.1
Release:    1
Summary:    Helper utility to launch KDE applications in sandbox
License:    GPLv2+
URL:        https://github.com/danvratil/ksbinit

Source0:    %{name}-%{version}.tar.xz

BuildRequires:  extra-cmake-modules
BuildRequires:  kf5-rpm-macros
BuildRequires:  qt5-qtbase-dev

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

%files
%doc COPYING README.md
%{_kf5_bindir}/ksbinit

%changelog
* Thu May 28 2015 Daniel Vrátil <dvratil@redhat.com> - 0.1-1
- Initial version
