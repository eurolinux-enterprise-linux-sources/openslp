Name:			openslp
Version:		2.0.0
Release:		7%{?dist}
Epoch:			1
Summary:		Open implementation of Service Location Protocol V2

Group:			System Environment/Libraries
License:		BSD
URL:			http://www.openslp.org
Source0:		http://downloads.sourceforge.net/openslp/%{name}-%{version}.tar.gz
# Source1,2: simple man pages (slightly modified help2man output)
Source1:		slpd.8.gz
Source2:		slptool.1.gz
# Source3: service file
Source3:		slpd.service
BuildRoot:		%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

# Patch0: creates script from upstream init script that sets multicast
#     prior to the start of the service
Patch0:			openslp-2.0.0-multicast-set.patch
# Patch1: fixes buffer overflow, rhbz#1181474
Patch1:			openslp-2.0.0-fortify-source-buffer-overflow.patch
# Patch2: fixes heap memory corruption in slpd/slpd_process.c, which allows
#   denial of service or potentially code execution,
#   backported form upstream, CVE-2017-17833
Patch2:  openslp-2.0.0-cve-2017-17833.patch

BuildRequires:		bison flex openssl-devel doxygen
BuildRequires:		automake libtool
BuildRequires:		systemd-units

%description
Service Location Protocol is an IETF standards track protocol that
provides a framework to allow networking applications to discover the
existence, location, and configuration of networked services in
enterprise networks.

OpenSLP is an open source implementation of the SLPv2 protocol as defined
by RFC 2608 and RFC 2614.

%package server
Summary:		OpenSLP server daemon
Group:			System Environment/Daemons
Requires:		%{name} = %{epoch}:%{version}-%{release}
Requires:		/bin/netstat
Requires(preun):	chkconfig, /sbin/service
Requires(post):		chkconfig
Requires(postun):	/sbin/service

%description server
Service Location Protocol is an IETF standards track protocol that
provides a framework that allows networking applications to discover
the existence, location, and configuration of networked services in
enterprise networks.

This package contains the SLP server. Every system, which provides any
services that should be used via an SLP client must run this server and
register the service.

%package devel
Summary:		OpenSLP headers and libraries
Group:			Development/Libraries
Requires:		%{name} = %{epoch}:%{version}-%{release}

%description devel
Service Location Protocol is an IETF standards track protocol that
provides a framework that allows networking applications to discover
the existence, location, and configuration of networked services in
enterprise networks.

This package contains header and library files to compile applications
with SLP support. It also contains developer documentation to develop
such applications.

%prep
%setup -q
%patch0 -p1 -b .multicast-set
%patch1 -p1 -b .fortify-source-buffer-overflow
%patch2 -p1 -b .cve-2017-17833


%build
export CFLAGS="-fPIC -fno-strict-aliasing -fPIE -DPIE $RPM_OPT_FLAGS"
export LDFLAGS="-pie -Wl,-z,now"
%configure \
  --prefix=%{_prefix} \
  --libdir=%{_libdir} \
  --sysconfdir=%{_sysconfdir} \
  --enable-async-api \
  --disable-rpath \
  --enable-slpv2-security \
  --localstatedir=/var
make %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT
mkdir -p ${RPM_BUILD_ROOT}/%{_sysconfdir}/slp.reg.d
# install script that sets multicast
mkdir -p ${RPM_BUILD_ROOT}/usr/lib/%{name}-server
install -m 0755 etc/slpd.all_init ${RPM_BUILD_ROOT}/usr/lib/%{name}-server/slp-multicast-set.sh
# install service file
mkdir -p ${RPM_BUILD_ROOT}/%{_unitdir}
install -p -m 644 %{SOURCE3} ${RPM_BUILD_ROOT}/%{_unitdir}/slpd.service
# install man page
mkdir -p ${RPM_BUILD_ROOT}/%{_mandir}/man8/
mkdir -p ${RPM_BUILD_ROOT}/%{_mandir}/man1/
cp %SOURCE1 ${RPM_BUILD_ROOT}/%{_mandir}/man8/
cp %SOURCE2 ${RPM_BUILD_ROOT}/%{_mandir}/man1/
rm -f  $RPM_BUILD_ROOT%{_libdir}/lib*.a
rm -f  $RPM_BUILD_ROOT%{_libdir}/lib*.la


%clean
rm -rf $RPM_BUILD_ROOT


%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%post server
%systemd_post slpd.service

%postun server
%systemd_postun_with_restart slpd.service

%preun server
%systemd_preun slpd.service


%files
%defattr(-,root,root,-)
%doc AUTHORS COPYING ChangeLog NEWS README
%doc doc/doc/*
%{_libdir}/libslp.so.*
%{_bindir}/slptool
%config(noreplace) %{_sysconfdir}/slp.conf
%config(noreplace) %{_sysconfdir}/slp.spi
%{_mandir}/man1/*

%files server
%defattr(-,root,root,-)
%dir /%{_sysconfdir}/slp.reg.d/
%dir /usr/lib/%{name}-server
/usr/lib/%{name}-server/slp-multicast-set.sh
%{_sbindir}/slpd
%config(noreplace) %{_sysconfdir}/slp.reg
%{_unitdir}/slpd.service
%{_mandir}/man8/*

%files devel
%defattr(-,root,root,-)
%{_includedir}/slp.h
%{_libdir}/libslp.so


%changelog
* Tue Jul 03 2018 Vitezslav Crhonek <vcrhonek@redhat.com> - 1:2.0.0-7
- Fix possible heap memory corruption, CVE-2017-17833
  Resolves: #1575698

* Tue Jun 28 2016 Vitezslav Crhonek <vcrhonek@redhat.com> - 1:2.0.0-6
- Fix buffer overflow termination of slpd with -D_FORTIFY_SOURCE=2
  Resolves: #1181474

* Fri Jan 24 2014 Daniel Mach <dmach@redhat.com> - 1:2.0.0-5
- Mass rebuild 2014-01-24

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 1:2.0.0-4
- Mass rebuild 2013-12-27

* Wed Oct 16 2013 Vitezslav Crhonek <vcrhonek@redhat.com> - 1:2.0.0-3
- Fix full relro
  Resolves: #881226

* Mon Jul 15 2013 Vitezslav Crhonek <vcrhonek@redhat.com> - 1:2.0.0-2
- Fix -devel requires

* Tue Jun 25 2013 Vitezslav Crhonek <vcrhonek@redhat.com> - 1:2.0.0-1
- Update to openslp-2.0.0
- Add systemd support
- Require /bin/netstat

* Wed May 15 2013 Vitezslav Crhonek <vcrhonek@redhat.com> - 2.0-0.3.beta2
- Add man pages for slptool and slpd
- Add CFLAGS and LDFLAGS for full relro

* Thu Jul 28 2011 Vitezslav Crhonek <vcrhonek@redhat.com> - 2.0-0.2.beta2
- Build with -fno-strict-aliasing

* Wed Jul 20 2011 Vitezslav Crhonek <vcrhonek@redhat.com> - 2.0-0.1.beta2
- Fix N-V-R

* Wed Jul 20 2011 Vitezslav Crhonek <vcrhonek@redhat.com> - 2.0.beta2-2
- Build

* Tue Jul 19 2011 Vitezslav Crhonek <vcrhonek@redhat.com> - 2.0.beta2-1
- Initial support
