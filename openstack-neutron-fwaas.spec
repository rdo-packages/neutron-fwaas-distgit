%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
%global modulename neutron_fwaas
%global servicename neutron-fwaas
%global type FWaaS

%global common_desc This is a %{type} service plugin for Openstack Neutron (Networking) service.

Name:           openstack-%{servicename}
Version:        XXX
Release:        XXX%{?dist}
Epoch:          1
Summary:        Openstack Networking %{type} plugin

License:        ASL 2.0
URL:            http://launchpad.net/neutron/
Source0:        https://tarballs.openstack.org/%{servicename}/%{servicename}-%{upstream_version}.tar.gz

BuildArch:      noarch
BuildRequires:  gawk
BuildRequires:  openstack-macros
BuildRequires:  python3-devel
BuildRequires:  python3-neutron >= 1:14.0.0
BuildRequires:  python3-pbr > 4.0.0
BuildRequires:  git-core

Requires:       ipset
Requires:       iptables
Requires:       python3-%{servicename} = %{epoch}:%{version}-%{release}
Requires:       openstack-neutron >= 1:14.0.0

%description
%{common_desc}


%package -n python3-%{servicename}
Summary:        Neutron %{type} Python libraries
%{?python_provide:%python_provide python3-%{servicename}}
Group:          Applications/System

Requires:       python3-neutron >= 1:14.0.0
Requires:       python3-alembic >= 0.8.10
Requires:       python3-eventlet
Requires:       python3-netaddr >= 0.7.18
Requires:       python3-neutron-lib >= 1.26.0
Requires:       python3-os-ken >= 0.3.0
Requires:       python3-oslo-config >= 2:5.2.0
Requires:       python3-oslo-db >= 4.37.0
Requires:       python3-oslo-log >= 3.36.0
Requires:       python3-oslo-messaging >= 5.29.0
Requires:       python3-oslo-privsep >= 1.32.0
Requires:       python3-oslo-service >= 1.24.0
Requires:       python3-oslo-utils >= 3.33.0
Requires:       python3-pbr
Requires:       python3-pyroute2 >= 0.5.3
Requires:       python3-requests
Requires:       python3-six >= 1.10.0
Requires:       python3-sqlalchemy >= 1.2.0

Requires:       python3-zmq >= 14.3.1


%description -n python3-%{servicename}
%{common_desc}

This package contains the Neutron %{type} Python library.


%package -n python3-%{servicename}-tests
Summary:        Neutron %{type} tests
%{?python_provide:%python_provide python3-%{servicename}-tests}
Group:          Applications/System

Requires:       python3-%{servicename} = %{epoch}:%{version}-%{release}


%description -n python3-%{servicename}-tests
%{common_desc}

This package contains Neutron %{type} test files.


%prep
%autosetup -n %{servicename}-%{upstream_version} -S git

# Let's handle dependencies ourselves
%py_req_cleanup

# Kill egg-info in order to generate new SOURCES.txt
rm -rf %{modulename}.egg-info

%build
export PBR_VERSION=%{version}
export SKIP_PIP_INSTALL=1
%{py3_build}

# Generate configuration files
PYTHONPATH=.
for file in `ls etc/oslo-config-generator/*`; do
    oslo-config-generator --config-file=$file
done

find etc -name *.sample | while read filename
do
    filedir=$(dirname $filename)
    file=$(basename $filename .sample)
    mv ${filename} ${filedir}/${file}
done

%install
export PBR_VERSION=%{version}
export SKIP_PIP_INSTALL=1
%{py3_install}

# Move config files to proper location
install -d -m 755 %{buildroot}%{_sysconfdir}/neutron

# The generated config files are not moved automatically by setup.py
mv etc/*.ini %{buildroot}%{_sysconfdir}/neutron

# Create and populate distribution configuration directory for L3/VPN agent
mkdir -p %{buildroot}%{_datadir}/neutron/l3_agent
ln -s %{_sysconfdir}/neutron/fwaas_driver.ini %{buildroot}%{_datadir}/neutron/l3_agent/fwaas_driver.conf

# Move rootwrap files to proper location
install -d -m 755 %{buildroot}%{_datarootdir}/neutron/rootwrap
mv %{buildroot}/usr/etc/neutron/rootwrap.d/*.filters %{buildroot}%{_datarootdir}/neutron/rootwrap


%files
%license LICENSE
%doc AUTHORS CONTRIBUTING.rst README.rst
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/fwaas_driver.ini
%{_datadir}/neutron/l3_agent/*.conf
%{_bindir}/neutron-fwaas-migrate-v1-to-v2
# TODO: see https://review.openstack.org/315826 for details, conflicts with core L3 agent
%exclude %{_bindir}/neutron-l3-agent

%files -n python3-%{servicename}
%{python3_sitelib}/%{modulename}
%{python3_sitelib}/%{modulename}-%{version}-py*.egg-info
%exclude %{python3_sitelib}/%{modulename}/tests
%{_datarootdir}/neutron/rootwrap/fwaas-privsep.filters


%files -n python3-%{servicename}-tests
%{python3_sitelib}/%{modulename}/tests

%changelog

