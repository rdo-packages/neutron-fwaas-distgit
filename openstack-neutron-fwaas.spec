# Macros for py2/py3 compatibility
%if 0%{?fedora} || 0%{?rhel} > 7
%global pyver %{python3_pkgversion}
%else
%global pyver 2
%endif
%global pyver_bin python%{pyver}
%global pyver_sitelib %python%{pyver}_sitelib
%global pyver_install %py%{pyver}_install
%global pyver_build %py%{pyver}_build
# End of macros for py2/py3 compatibility
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
BuildRequires:  python%{pyver}-devel
BuildRequires:  python%{pyver}-neutron >= 1:14.0.0
BuildRequires:  python%{pyver}-pbr > 4.0.0
BuildRequires:  git

Requires:       ipset
Requires:       iptables
Requires:       python%{pyver}-%{servicename} = %{epoch}:%{version}-%{release}
Requires:       openstack-neutron >= 1:14.0.0

%description
%{common_desc}


%package -n python%{pyver}-%{servicename}
Summary:        Neutron %{type} Python libraries
%{?python_provide:%python_provide python%{pyver}-%{servicename}}
Group:          Applications/System

Requires:       python%{pyver}-neutron >= 1:14.0.0
Requires:       python%{pyver}-alembic >= 0.8.10
Requires:       python%{pyver}-eventlet
Requires:       python%{pyver}-netaddr >= 0.7.18
Requires:       python%{pyver}-neutron-lib >= 1.26.0
Requires:       python%{pyver}-os-ken >= 0.3.0
Requires:       python%{pyver}-oslo-config >= 2:5.2.0
Requires:       python%{pyver}-oslo-db >= 4.37.0
Requires:       python%{pyver}-oslo-log >= 3.36.0
Requires:       python%{pyver}-oslo-messaging >= 5.29.0
Requires:       python%{pyver}-oslo-privsep >= 1.32.0
Requires:       python%{pyver}-oslo-service >= 1.24.0
Requires:       python%{pyver}-oslo-utils >= 3.33.0
Requires:       python%{pyver}-pbr
Requires:       python%{pyver}-pyroute2 > 0.4.21
Requires:       python%{pyver}-requests
Requires:       python%{pyver}-six >= 1.10.0
Requires:       python%{pyver}-sqlalchemy >= 1.2.0

# Handle python2 exception
%if %{pyver} == 2
Requires:       python-zmq >= 14.3.1
%else
Requires:       python%{pyver}-zmq >= 14.3.1
%endif


%description -n python%{pyver}-%{servicename}
%{common_desc}

This package contains the Neutron %{type} Python library.


%package -n python%{pyver}-%{servicename}-tests
Summary:        Neutron %{type} tests
%{?python_provide:%python_provide python%{pyver}-%{servicename}-tests}
Group:          Applications/System

Requires:       python%{pyver}-%{servicename} = %{epoch}:%{version}-%{release}


%description -n python%{pyver}-%{servicename}-tests
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
%{pyver_build}

# Generate configuration files
PYTHONPATH=.
for file in `ls etc/oslo-config-generator/*`; do
    oslo-config-generator-%{pyver} --config-file=$file
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
%{pyver_install}

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

%files -n python%{pyver}-%{servicename}
%{pyver_sitelib}/%{modulename}
%{pyver_sitelib}/%{modulename}-%{version}-py*.egg-info
%exclude %{pyver_sitelib}/%{modulename}/tests
%{_datarootdir}/neutron/rootwrap/fwaas-privsep.filters


%files -n python%{pyver}-%{servicename}-tests
%{pyver_sitelib}/%{modulename}/tests

%changelog

