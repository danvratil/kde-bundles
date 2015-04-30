Name:       marble
Version:    15.04.0
Release:    1
Summary:    KDE Virtual Globe application
License:    LGPLv2+ nad GPL3
URL:        https://projects.kde.org/kdeedu/marble

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
BuildRequires:  qt5-qtsvg-dev
BuildRequires:  qt5-qtscript-dev
BuildRequires:  qt5-qtxmlpatterns-dev


%description
Marble is a Virtual Globe and World Atlas that you can use to learn more
about Earth: You can pan and zoom around and you can look up places and
roads. A mouse click on a place label will provide the respective
Wikipedia article.


%prep
%setup -q -n %{name}-%{version}

%build
mkdir %{_target_platform}
pushd %{_target_platform}
%{cmake_kf5} .. -DQT5BUILD=TRUE
popd

make %{?_smp_mflags} -C %{_target_platform}


%install
make install/fast DESTDIR=%{buildroot} -C %{_target_platform}


%check


%files
%doc COPYING COPYING.LIB


