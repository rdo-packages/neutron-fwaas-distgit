%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
%global modulename neutron_fwaas
%global servicename neutron-fwaas
%{?dlrn: %global tarsources neutron-fwaas}
%{!?dlrn: %global tarsources neutron_fwaas}
%global type FWaaS

# we are excluding some BRs from automatic generator
%global excluded_brs doc8 bandit pre-commit hacking flake8-import-order isort pylint sphinx openstackdocstheme

%global common_desc This is a %{type} service plugin for Openstack Neutron (Networking) service.

Name:           openstack-%{servicename}
Version:        20.0.1
Release:        1%{?dist}
Epoch:          1
Summary:        Openstack Networking %{type} plugin

License:        Apache-2.0
URL:            http://launchpad.net/neutron/
Source0:        https://tarballs.openstack.org/%{servicename}/%{tarsources}-%{upstream_version}.tar.gz

BuildArch:      noarch
BuildRequires:  pyproject-rpm-macros
BuildRequires:  git-core
BuildRequires:  openstack-macros
BuildRequires:  python3-devel

Requires:       python3-%{servicename} = %{epoch}:%{version}-%{release}
Requires:       openstack-neutron >= %{epoch}:23.0.0
Requires:       ipset
Requires:       iptables

%description
%{common_desc}


%package -n python3-%{servicename}
Summary:        Neutron %{type} Python libraries
%{?python_provide:%python_provide python3-%{servicename}}
Group:          Applications/System


%description -n python3-%{servicename}
%{common_desc}

This package contains the Neutron %{type} Python library.


%package -n python3-%{servicename}-tests
Summary:        Neutron %{type} tests
%{?python_provide:%python_provide python3-%{servicename}-tests}
Group:          Applications/System


%description -n python3-%{servicename}-tests
%{common_desc}

This package contains Neutron %{type} test files.


%prep
%autosetup -n %{tarsources}-%{upstream_version} -S git

# do not run linters
sed -i /^[[:space:]]*-c{env:.*_CONSTRAINTS_FILE.*/d tox.ini
sed -i "s/^deps = -c{env:.*_CONSTRAINTS_FILE.*/deps =/" tox.ini
sed -i /^minversion.*/d tox.ini
sed -i /^requires.*virtualenv.*/d tox.ini
sed -i '/^  hacking.*/d' tox.ini

# Exclude some bad-known BRs
for pkg in %{excluded_brs}; do
  for reqfile in doc/requirements.txt test-requirements.txt; do
    if [ -f $reqfile ]; then
      sed -i /^${pkg}.*/d $reqfile
    fi
  done
done

%generate_buildrequires
%pyproject_buildrequires -t -e %{default_toxenv}

# Kill egg-info in order to generate new SOURCES.txt
rm -rf %{modulename}.egg-info

%build
export PBR_VERSION=%{version}
export SKIP_PIP_INSTALL=1
%pyproject_wheel

%install
%pyproject_install

# Generate configuration files
export PYTHONPATH="%{buildroot}/%{python3_sitelib}"
for file in `ls etc/oslo-config-generator/*`; do
    oslo-config-generator --config-file=$file
done

find etc -name *.sample | while read filename
do
    filedir=$(dirname $filename)
    file=$(basename $filename .sample)
    mv ${filename} ${filedir}/${file}
done

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

%files -n python3-%{servicename}
%{python3_sitelib}/%{modulename}
%{python3_sitelib}/%{modulename}-%{version}.dist-info
%exclude %{python3_sitelib}/%{modulename}/tests
%{_datarootdir}/neutron/rootwrap/fwaas-privsep.filters


%files -n python3-%{servicename}-tests
%{python3_sitelib}/%{modulename}/tests

%changelog
* Fri Jul 25 2025 RDO <dev@lists.rdoproject.org> 1:20.0.1-1
- Update to 20.0.1


