# Run tests (requires network connectivity)
%global with_check 0

# Prebuilt binaries break build process for CentOS. Disable debug packages to resolve
%if 0%{?rhel}
%define debug_package %{nil}
%endif

%global provider        github
%global provider_tld    com
%global project         prometheus
%global repo            blackbox_exporter
# https://github.com/prometheus/blackbox_exporter/
%global provider_prefix %{provider}.%{provider_tld}/%{project}/%{repo}
%global import_path     %{provider_prefix}

Name:           golang-%{provider}-%{project}-%{repo}
Version:        0.14.0
Release:        1%{?dist}
Summary:        Blackbox prober exporter
License:        ASL 2.0
URL:            https://%{provider_prefix}
Source0:        https://%{provider_prefix}/archive/v%{version}.tar.gz
Source1:        blackbox_exporter.service

Provides:       blackbox_exporter = %{version}-%{release}

%if 0%{?rhel} != 6
BuildRequires:  systemd
%endif

# e.g. el6 has ppc64 arch without gcc-go, so EA tag is required
ExclusiveArch:  %{?go_arches:%{go_arches}}%{!?go_arches:%{ix86} x86_64 aarch64 %{arm}}
# If go_compiler is not set to 1, there is no virtual provide. Use golang instead.
BuildRequires:  %{?go_compiler:compiler(go-compiler)}%{!?go_compiler:golang}

%description
The blackbox exporter allows blackbox probing of endpoints over HTTP, HTTPS, DNS, TCP and ICMP

%prep
%setup -q -n %{repo}-%{version}

%build
export GO111MODULE=on
go build -ldflags=-linkmode=external -mod vendor -o blackbox_exporter

%install
%if 0%{?rhel} != 6
install -d -p   %{buildroot}%{_unitdir}
%endif

install -Dpm 0644 blackbox.yml %{buildroot}%{_sysconfdir}/blackbox_exporter/blackbox.yml
install -Dpm 0755 blackbox_exporter %{buildroot}%{_sbindir}/blackbox_exporter
%if 0%{?rhel} != 6
install -Dpm 0644 %{SOURCE1} %{buildroot}%{_unitdir}/blackbox_exporter.service
%endif

%if 0%{?with_check}
%check
export GO111MODULE=on
go test -mod vendor
%endif


%files
%if 0%{?rhel} != 6
%{_unitdir}/blackbox_exporter.service
%endif
%attr(0640, blackbox_exporter, blackbox_exporter) %config(noreplace) %{_sysconfdir}/blackbox_exporter/blackbox.yml
%license LICENSE
%doc README.md
%attr(0755, root, root) %caps(cap_net_raw=ep) %{_sbindir}/blackbox_exporter

%pre
getent group blackbox_exporter > /dev/null || groupadd -r blackbox_exporter
getent passwd blackbox_exporter > /dev/null || \
    useradd -rg blackbox_exporter -s /sbin/nologin \
            -c "blackbox Prometheus exporter" blackbox_exporter

%post
%if 0%{?rhel} != 6
%systemd_post blackbox_exporter.service
%endif

%preun
%if 0%{?rhel} != 6
%systemd_preun blackbox_exporter.service
%endif

%postun
%if 0%{?rhel} != 6
%systemd_postun blackbox_exporter.service
%endif

%changelog
