## enable experimental cmake build support (or not)
## still lacks some features, like visibility
#define cmake_build 1

Summary:        Exif and Iptc metadata manipulation library
Name:	        exiv2
Version:        0.24
Release:        1%{?dist}

License:        GPLv2+
URL: 	        http://www.exiv2.org/
Source0:        http://www.exiv2.org/exiv2-%{version}%{?pre:-%{pre}}.tar.gz

## upstream patches
# CVE-2014-9449 exiv2: buffer overflow in RiffVideo::infoTagsHandler
# https://bugzilla.redhat.com/show_bug.cgi?id=1178908
# http://dev.exiv2.org/issues/960
# commit: http://dev.exiv2.org/projects/exiv2/repository/diff?rev=3264&rev_to=3263
Patch100:       exiv2-0.24-CVE-2014-9449.patch

## upstreamable patches

BuildRequires:  expat-dev
BuildRequires:  gettext
BuildRequires:  pkgconfig
BuildRequires:  zlib-dev
# docs
#BuildRequires:  doxygen graphviz libxslt

Requires:       %{name}-libs%{?_isa} = %{version}-%{release}

%description
A command line utility to access image metadata, allowing one to:
* print the Exif metadata of Jpeg images as summary info, interpreted values,
  or the plain data for each tag
* print the Iptc metadata of Jpeg images
* print the Jpeg comment of Jpeg images
* set, add and delete Exif and Iptc metadata of Jpeg images
* adjust the Exif timestamp (that's how it all started...)
* rename Exif image files according to the Exif timestamp
* extract, insert and delete Exif metadata (including thumbnails),
  Iptc metadata and Jpeg comments

%package dev
Summary:        Header files, libraries and development documentation for %{name}
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}
%description    dev
%{summary}.

%package        libs
Summary:        Exif and Iptc metadata manipulation library
%description libs
A C++ library to access image metadata, supporting full read and write access
to the Exif and Iptc metadata, Exif MakerNote support, extract and delete
methods for Exif thumbnails, classes to access Ifd and so on.


%prep
%setup -q -n %{name}-%{version}%{?pre:-%{pre}}

%patch100 -p1 -b .CVE-2014-9449

#%patch50 -p1 -b .cmake_LIB_SUFFIX
#%patch51 -p1 -b .cmake_mandir
#%patch52 -p1 -b .doxygen_config


%build
%configure \
    --disable-rpath \
    --disable-static

sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool

make %{?_smp_mflags}


%install
make install DESTDIR=%{buildroot}

## fix perms on installed lib
ls -l     %{buildroot}%{_libdir}/libexiv2.so.*
chmod 755 %{buildroot}%{_libdir}/libexiv2.so.*


%find_lang exiv2

## unpackaged files
rm -fv %{buildroot}%{_libdir}/pkgconfig/exiv2.lsm
rm -fv %{buildroot}%{_libdir}/libexiv2.la


%check
export PKG_CONFIG_PATH=%{buildroot}%{_libdir}/pkgconfig
test "$(pkg-config --modversion exiv2)" = "%{version}"
test -x %{buildroot}%{_libdir}/libexiv2.so


%files
%doc COPYING README
%{_bindir}/exiv2
%{_mandir}/man1/*

%post libs -p /sbin/ldconfig
%postun libs -p /sbin/ldconfig

%files libs -f exiv2.lang
%{_libdir}/libexiv2.so.13*

%files dev
%{_includedir}/exiv2/
%{_libdir}/libexiv2.so
%{_libdir}/pkgconfig/exiv2.pc

%changelog
* Tue May 05 2015 Daniel Vrátil <dvratil@redhat.com> - 0.24-1
- Initial version (forked from Fedora)
