Summary:        Library for reading RAW files obtained from digital photo cameras
Name:           LibRaw
Version:        0.16.0
Release:        1%{?dist}
License:        GPLv3+
Group:          Development/Libraries
URL:            http://www.libraw.org

#BuildRequires:  lcms2-dev
#BuildRequires:  jasper-dev

Source0:        http://www.libraw.org/data/%{name}-%{version}.tar.gz
Source1:        http://www.libraw.org/data/%{name}-demosaic-pack-GPL2-%{version}.tar.gz
Source2:        http://www.libraw.org/data/%{name}-demosaic-pack-GPL3-%{version}.tar.gz
Patch0:         LibRaw-0.6.0-pkgconfig.patch

%description
LibRaw is a library for reading RAW files obtained from digital photo
cameras (CRW/CR2, NEF, RAF, DNG, and others).

LibRaw is based on the source codes of the dcraw utility, where part of
drawbacks have already been eliminated and part will be fixed in future.

%package dev
Summary:        LibRaw development libraries
Group:          Development/Libraries
Requires:   %{name} = %{version}-%{release}

%description dev
LibRaw development libraries.

This package contains libraries that applications can use to build
against LibRaw.

%package static
Summary:        LibRaw static development libraries
Group:          Development/Libraries

%description static
LibRaw static development libraries.

%prep
%setup -q -a1 -a2

%patch0 -p0 -b .pkgconfig

%build
%configure --enable-examples=no \
           --disable-jasper \
           --disable-lcms \
	       --enable-demosaic-pack-gpl2 \
           --enable-demosaic-pack-gpl3
make %{?_smp_mflags}

%install
cp -pr doc manual
chmod 644 LICENSE.CDDL LICENSE.LGPL COPYRIGHT Changelog.txt Changelog.rus
chmod 644 manual/*.html

# The Libraries
make install DESTDIR=%{buildroot}

%files
%defattr(-,root,root,-)
%doc LICENSE.CDDL LICENSE.LGPL COPYRIGHT Changelog.txt Changelog.rus
%{_libdir}/*.so.*

%files static
%defattr(-,root,root,-)
%{_libdir}/*.a

%files dev
%defattr(-,root,root,-)
%doc manual
%doc samples
%dir %{_includedir}/libraw
%{_includedir}/libraw/*.h
%{_libdir}/*.so
%{_libdir}/pkgconfig/*.pc
%exclude %{_libdir}/*.la
%exclude %{_docdir}/libraw/*

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%changelog
* Tue May 05 2015 Daniel Vrátil <dvratil@redhat.com> - 0.16.0-1
- Initial version (forked from Fedora)
