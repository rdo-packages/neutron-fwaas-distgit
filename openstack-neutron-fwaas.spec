%global milestone .0rc1
%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
%global modulename neutron_fwaas
%global servicename neutron-fwaas
%global type FWaaS

%global common_desc This is a %{type} service plugin for Openstack Neutron (Networking) service.

%define major_version %(echo %{version} | awk 'BEGIN { FS=\".\"}; {print $1}')
%define next_version %(echo $((%{major_version} + 1)))

Name:           openstack-%{servicename}
Version:        13.0.0
Release:        0.1%{?milestone}%{?dist}
Epoch:          1
Summary:        Openstack Networking %{type} plugin

License:        ASL 2.0
URL:            http://launchpad.net/neutron/
Source0:        https://tarballs.openstack.org/%{servicename}/%{servicename}-%{upstream_version}.tar.gz

#
# patches_base=13.0.0.0rc1
#

BuildArch:      noarch
BuildRequires:  gawk
BuildRequires:  openstack-macros
BuildRequires:  python2-devel
BuildRequires:  python-neutron >= %{epoch}:%{major_version}
BuildConflicts: python-neutron >= %{epoch}:%{next_version}
BuildRequires:  python2-pbr
BuildRequires:  git

Requires:       ipset
Requires:       iptables
Requires:       python-%{servicename} = %{epoch}:%{version}-%{release}
Requires:       openstack-neutron >= %{epoch}:%{major_version}
Conflicts:      openstack-neutron >= %{epoch}:%{next_version}

%description
%{common_desc}


%package -n python-%{servicename}
Summary:        Neutron %{type} Python libraries
Group:          Applications/System

Requires:       python-neutron >= %{epoch}:%{major_version}
Conflicts:      python-neutron >= %{epoch}:%{next_version}
Requires:       python2-alembic >= 0.8.10
Requires:       python2-eventlet
Requires:       python2-netaddr >= 0.7.18
Requires:       python-neutron-lib >= 1.18.0
Requires:       python2-oslo-config >= 2:5.2.0
Requires:       python2-oslo-db >= 4.27.0
Requires:       python2-oslo-log >= 3.36.0
Requires:       python2-oslo-messaging >= 5.29.0
Requires:       python2-oslo-privsep >= 1.23.0
Requires:       python2-oslo-service >= 1.24.0
Requires:       python2-oslo-utils >= 3.33.0
Requires:       python2-pbr
Requires:       python2-pyroute2
Requires:       python2-requests
Requires:       python2-six >= 1.10.0
Requires:       python2-sqlalchemy >= 1.0.10
Requires:       python-zmq >= 14.3.1


%description -n python-%{servicename}
%{common_desc}

This package contains the Neutron %{type} Python library.


%package -n python-%{servicename}-tests
Summary:        Neutron %{type} tests
Group:          Applications/System

Requires:       python-%{servicename} = %{epoch}:%{version}-%{release}


%description -n python-%{servicename}-tests
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
%{__python2} setup.py build

# Generate configuration files
PYTHONPATH=. tools/generate_config_file_samples.sh
find etc -name *.sample | while read filename
do
    filedir=$(dirname $filename)
    file=$(basename $filename .sample)
    mv ${filename} ${filedir}/${file}
done

%install
export PBR_VERSION=%{version}
export SKIP_PIP_INSTALL=1
%{__python2} setup.py install -O1 --skip-build --root %{buildroot}

# Create fake egg-info for the tempest plugin
%py2_entrypoint %{modulename} %{servicename}

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
# TODO: see https://review.openstack.org/315826 for details, conflicts with core L3 agent
%exclude %{_bindir}/neutron-l3-agent

%files -n python-%{servicename}
%{python2_sitelib}/%{modulename}
%{python2_sitelib}/%{modulename}-%{version}-py%{python2_version}.egg-info
%exclude %{python2_sitelib}/%{modulename}/tests
%{_datarootdir}/neutron/rootwrap/fwaas-privsep.filters


%files -n python-%{servicename}-tests
%{python2_sitelib}/%{modulename}/tests
%{python2_sitelib}/%{modulename}_tests.egg-info

%changelog
* Mon Aug 20 2018 RDO <dev@lists.rdoproject.org> 1:13.0.0-0.1.0rc1
- Update to 13.0.0.0rc1


