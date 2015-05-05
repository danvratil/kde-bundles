Summary:	    Library for reading and writing sound files
Name:		    libsndfile
Version:	    1.0.25
Release:	    1%{?dist}
License:	    LGPLv2+ and GPLv2+ and BSD
Group:		    System Environment/Libraries
URL:		    http://www.mega-nerd.com/libsndfile/
Source0:	    http://www.mega-nerd.com/libsndfile/files/libsndfile-%{version}.tar.gz
Patch0:		    %{name}-1.0.25-system-gsm.patch
Patch1:         libsndfile-1.0.25-zerodivfix.patch
Patch2:         libsndfile-1.0.25-cve2014_9496.patch

BuildRequires:	alsa-lib-dev
#BuildRequires:	flac-devel
BuildRequires:	libogg-dev
BuildRequires:	libvorbis-dev
BuildRequires:	gsm-dev
#BuildRequires:	libtool


%description
libsndfile is a C library for reading and writing sound files such as
AIFF, AU, WAV, and others through one standard interface. It can
currently read/write 8, 16, 24 and 32-bit PCM files as well as 32 and
64-bit floating point WAV files and a number of compressed formats. It
compiles and runs on *nix, MacOS, and Win32.


%package dev
Summary:	Development files for libsndfile
Group:		Development/Libraries
Requires:	%{name}%{?_isa} = %{version}-%{release} pkgconfig


%description dev
libsndfile is a C library for reading and writing sound files such as
AIFF, AU, WAV, and others through one standard interface.
This package contains files needed to develop with libsndfile.


%package utils
Summary:	Command Line Utilities for libsndfile
Group:		Applications/Multimedia
Requires:	%{name} = %{version}-%{release}
Obsoletes:	libsndfile < 1.0.20-4


%description utils
libsndfile is a C library for reading and writing sound files such as
AIFF, AU, WAV, and others through one standard interface.
This package contains command line utilities for libsndfile.


%prep
%setup -q
%patch0 -p1
%patch1 -p1 -b .zerodivfix
%patch2 -p1 -b .cve2014_9496
rm -r src/GSM610 ; autoreconf -I M4 -fiv # for system-gsm patch

%build
%configure \
	--disable-dependency-tracking \
	--enable-sqlite \
	--enable-alsa \
	--enable-largefile \
	--disable-static

# Get rid of rpath
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool

make %{?_smp_mflags}


%install
make install DESTDIR=$RPM_BUILD_ROOT
rm -rf __docs
cp -pR $RPM_BUILD_ROOT%{_docdir}/libsndfile1-dev/html __docs
rm -rf $RPM_BUILD_ROOT%{_docdir}/libsndfile1-dev

# fix multilib issues
%if %{__isa_bits} == 64
%define wordsize 64
%else
%define wordsize 32
%endif

mv %{buildroot}%{_includedir}/sndfile.h \
   %{buildroot}%{_includedir}/sndfile-%{wordsize}.h

cat > %{buildroot}%{_includedir}/sndfile.h <<EOF
#include <bits/wordsize.h>

#if __WORDSIZE == 32
# include "sndfile-32.h"
#elif __WORDSIZE == 64
# include "sndfile-64.h"
#else
# error "unexpected value for __WORDSIZE macro"
#endif
EOF

%if 0%{?rhel} != 0
rm -f %{buildroot}%{_bindir}/sndfile-jackplay
%endif


%check
#LD_LIBRARY_PATH=$PWD/src/.libs make check


%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig


%files
%doc COPYING AUTHORS README NEWS
%{_libdir}/%{name}.so.*

%files utils
%{_bindir}/sndfile-cmp
%{_bindir}/sndfile-concat
%{_bindir}/sndfile-convert
%{_bindir}/sndfile-deinterleave
%{_bindir}/sndfile-info
%{_bindir}/sndfile-interleave
%{_bindir}/sndfile-metadata-get
%{_bindir}/sndfile-metadata-set
%{_bindir}/sndfile-play
%{_bindir}/sndfile-regtest
%{_bindir}/sndfile-salvage
%{_mandir}/man1/sndfile-cmp.1*
%{_mandir}/man1/sndfile-concat.1*
%{_mandir}/man1/sndfile-convert.1*
%{_mandir}/man1/sndfile-deinterleave.1*
%{_mandir}/man1/sndfile-info.1*
%{_mandir}/man1/sndfile-interleave.1*
%{_mandir}/man1/sndfile-metadata-get.1*
%{_mandir}/man1/sndfile-metadata-set.1*
%{_mandir}/man1/sndfile-play.1*

%files dev
%doc __docs/*
%doc ChangeLog
%exclude %{_libdir}/%{name}.la
%{_includedir}/sndfile.h
%{_includedir}/sndfile.hh
%{_includedir}/sndfile-%{wordsize}.h
%{_libdir}/%{name}.so
%{_libdir}/pkgconfig/sndfile.pc


%changelog
* Mon May 04 2015 Daniel Vrátil <dvratil@redhat.com> - 1.0.25-1
- Initial version (forked from Fedora)
