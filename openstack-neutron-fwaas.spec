%global modulename neutron_fwaas
%global servicename neutron-fwaas
%global type FWaaS

Name:           openstack-%{servicename}
Version:        XXX
Release:        XXX%{?dist}
Epoch:          1
Summary:        Openstack Networking %{type} plugin

License:        ASL 2.0
URL:            http://launchpad.net/neutron/
Source0:        http://tarballs.openstack.org/%{servicename}/%{servicename}-master.tar.gz

BuildArch:      noarch
BuildRequires:  python2-devel
BuildRequires:  python-neutron >= 1:8.0.0
BuildRequires:  python-pbr
BuildRequires:  python-setuptools
BuildRequires:	git

Requires:       ipset
Requires:       iptables
Requires:       python-%{servicename} = %{epoch}:%{version}-%{release}
Requires:       openstack-neutron >= 1:8.0.0

%description
This is a %{type} service plugin for Openstack Neutron (Networking) service.


%package -n python-%{servicename}
Summary:        Neutron %{type} Python libraries
Group:          Applications/System

Requires:       python-neutron >= 1:8.0.0
Requires:       python-alembic
Requires:       python-eventlet
Requires:       python-netaddr >= 0.7.12
Requires:       python-oslo-config >= 2:1.4.0
Requires:       python-oslo-db >= 1.1.0
Requires:       python-oslo-log >= 1.0.0
Requires:       python-oslo-messaging >= 1.4.0.0
Requires:       python-oslo-serialization >= 1.0.0
Requires:       python-oslo-utils >= 1.0.0
Requires:       python-pbr
Requires:       python-requests
Requires:       python-six
Requires:       python-sqlalchemy


%description -n python-%{servicename}
This is a %{type} service plugin for Openstack Neutron (Networking) service.

This package contains the Neutron %{type} Python library.


%package -n python-%{servicename}-tests
Summary:        Neutron %{type} tests
Group:          Applications/System

Requires:       python-%{servicename} = %{epoch}:%{version}-%{release}


%description -n python-%{servicename}-tests
This is a %{type} service plugin for Openstack Neutron (Networking) service.

This package contains Neutron %{type} test files.


%prep
%autosetup -n %{servicename}-%{upstream_version} -S git

# Let's handle dependencies ourselves
rm -f requirements.txt

# Kill egg-info in order to generate new SOURCES.txt
rm -rf neutron_fwaas.egg-info

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

# Move config files to proper location
install -d -m 755 %{buildroot}%{_sysconfdir}/neutron

# The generated config files are not moved automatically by setup.py
mv etc/*.ini %{buildroot}%{_sysconfdir}/neutron

# Create and populate distribution configuration directory for L3/VPN agent
mkdir -p %{buildroot}%{_datadir}/neutron/l3_agent
ln -s %{_sysconfdir}/neutron/fwaas_driver.ini %{buildroot}%{_datadir}/neutron/l3_agent/fwaas_driver.conf


%files
%license LICENSE
%doc AUTHORS CONTRIBUTING.rst README.rst
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/fwaas_driver.ini
%{_datadir}/neutron/l3_agent/*.conf


%files -n python-%{servicename}
%{python2_sitelib}/%{modulename}
%{python2_sitelib}/%{modulename}-%{version}-py%{python2_version}.egg-info
%exclude %{python2_sitelib}/%{modulename}/tests


%files -n python-%{servicename}-tests
%{python2_sitelib}/%{modulename}/tests


%changelog
