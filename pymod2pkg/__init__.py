#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from __future__ import print_function

import argparse
import platform
import re


class TranslationRule(object):
    pass


class SingleRule(TranslationRule):
    def __init__(self, mod, pkg, py3pkg=None, distmap=None):
        self.mod = mod
        self.pkg = pkg
        self.py3pkg = py3pkg if py3pkg else pkg
        self.distmap = distmap

    def __call__(self, mod, dist):
        if mod != self.mod:
            return None
        if self.distmap and dist:
            for distrex in self.distmap:
                if re.match(distrex, dist):
                    return self.distmap[distrex]
        return (self.pkg, self.py3pkg)


class MultiRule(TranslationRule):
    def __init__(self, mods, pkgfun):
        self.mods = mods
        self.pkgfun = pkgfun

    def __call__(self, mod, dist):
        if mod in self.mods:
            pkg, pkg3 = self.pkgfun(mod)
            return (pkg, pkg3)
        return None


class RegexRule(TranslationRule):
    def __init__(self, pattern, pkgfun):
        self.pattern = pattern
        self.pkgfun = pkgfun

    def __call__(self, mod, dist):
        if re.match(self.pattern, mod):
            pkg, pkg3 = self.pkgfun(mod)
            return (pkg, pkg3)
        return None


def default_rdo_tr(mod):
    pkg = mod.rsplit('-python')[0]
    pkg = pkg.replace('_', '-').replace('.', '-').lower()
    if not pkg.startswith('python-'):
        pkg = 'python-' + pkg
    pkg3 = re.sub('python', 'python3', pkg)
    return (pkg, pkg3)


def default_ubuntu_tr(mod):
    return ('python-' + mod.lower(), 'python3-' + mod.lower())


def default_suse_tr(mod):
    return ('python2-' + mod, 'python3-' + mod)


def openstack_prefix_tr(mod):
    return ('openstack-' + mod.lower(), '')


def rdo_horizon_plugins_tr(mod):
    mod = mod.replace('dashboard', 'ui')
    return ('openstack-' + mod, '')


def rdo_xstatic_tr(mod):
    mod = mod.replace('_', '-').replace('.', '-')
    return ('python-' + mod, 'python3-' + mod)


def same_name_python3_prefix(mod):
    return (mod, 'python3-' + mod)


def same_name_python_subst_python3(mod):
    pkg3 = re.sub('python', 'python3', mod)
    return (mod, pkg3)


def subst_python2_python3(mod):
    pkg2 = re.sub('python', 'python2', mod)
    pkg3 = re.sub('python', 'python3', mod)
    return (pkg2, pkg3)


def rdo_tempest_plugins_tr(mod):
    mod = mod.replace('tempest-plugin', 'tests-tempest')
    return ('python-' + mod, 'python3-' + mod)


RDO_PKG_MAP = [
    # This demonstrates per-dist filter
    # SingleRule('sphinx', 'python-sphinx',
    #           distmap={'epel-6': 'python-sphinx10'}),
    SingleRule('Babel', 'python-babel', 'python3-babel'),
    SingleRule('bandit', 'bandit'),
    SingleRule('distribute', 'python-setuptools', 'python3-setuptools'),
    SingleRule('dnspython', 'python-dns', 'python3-dns'),
    SingleRule('google-api-python-client', 'python-google-api-client',
               'python3-google-api-client'),
    SingleRule('GitPython', 'GitPython', 'python3-GitPython'),
    SingleRule('pyOpenSSL', 'pyOpenSSL', 'python3-pyOpenSSL'),
    SingleRule('IPy', 'python-IPy', 'python-IPy-python3'),
    SingleRule('pycrypto', 'python-crypto', 'python3-crypto'),
    SingleRule('pyzmq', 'python-zmq', 'python3-zmq'),
    SingleRule('mysql-python', 'MySQL-python', 'python3-mysql'),
    SingleRule('PyMySQL', 'python-PyMySQL', 'python3-PyMySQL'),
    SingleRule('PyJWT', 'python-jwt', 'python3-jwt'),
    SingleRule('MySQL-python', 'MySQL-python', 'python3-mysql'),
    SingleRule('PasteDeploy', 'python-paste-deploy', 'python3-paste-deploy'),
    SingleRule('sqlalchemy-migrate', 'python-migrate', 'python3-migrate'),
    SingleRule('qpid-python', 'python-qpid'),
    SingleRule('nosexcover', 'python-nose-xcover', 'python3-nose-xcover.'),
    SingleRule('posix_ipc', 'python-posix_ipc', 'python3-posix_ipc'),
    SingleRule('oslosphinx', 'python-oslo-sphinx', 'python3-oslo-sphinx'),
    SingleRule('ovs', 'python-openvswitch', 'python3-openvswitch'),
    SingleRule('pyinotify', 'python-inotify', 'python3-inotify'),
    SingleRule('pyScss', 'python-scss', 'python3-scss'),
    SingleRule('tripleo-incubator', 'openstack-tripleo'),
    SingleRule('pika-pool', 'python-pika_pool', 'python3-pika_pool'),
    SingleRule('suds-jurko', 'python-suds', 'python3-suds'),
    SingleRule('supervisor', 'supervisor', 'python3-supervisor'),
    SingleRule('wsgi_intercept', 'python-wsgi_intercept',
               'python3-wsgi_intercept'),
    SingleRule('Sphinx', 'python-sphinx', 'python3-sphinx'),
    SingleRule('xattr', 'pyxattr', 'python3-pyxattr'),
    SingleRule('XStatic-term.js', 'python-XStatic-termjs',
               'python3-XStatic-termjs'),
    SingleRule('horizon', 'openstack-dashboard'),
    SingleRule('networking-vsphere', 'openstack-neutron-vsphere'),
    SingleRule('m2crypto', 'm2crypto'),
    SingleRule('libvirt-python', 'libvirt-python', 'libvirt-python3'),
    SingleRule('tempest-horizon', 'python-horizon-tests-tempest'),
    MultiRule(
        mods=['PyYAML', 'numpy', 'pyflakes', 'pylint', 'pyparsing',
              'pystache', 'pytz', 'pysendfile'],
        pkgfun=same_name_python3_prefix),
    # OpenStack services
    MultiRule(
        # keep lists in alphabetic order
        mods=['aodh', 'barbican', 'ceilometer', 'cinder', 'cloudkitty',
              'designate', 'ec2-api', 'glance', 'heat', 'heat-templates',
              'ironic', 'ironic-discoverd', 'ironic-inspector',
              'ironic-python-agent', 'karbor', 'keystone', 'magnum', 'manila',
              'masakari', 'masakari-monitors', 'mistral', 'monasca-agent',
              'monasca-api', 'monasca-ceilometer', 'monasca-log-api',
              'monasca-notification', 'monasca-persister', 'monasca-transform',
              'murano', 'neutron', 'neutron-fwaas', 'neutron-lbaas',
              'neutron-vpnaas', 'nova', 'octavia', 'rally', 'sahara', 'swift',
              'Tempest', 'trove', 'tuskar', 'vitrage', 'zaqar'],
        pkgfun=openstack_prefix_tr),
    # Horizon plugins (normalized to openstack-<project>-ui)
    RegexRule(pattern=r'\w+-(dashboard|ui)', pkgfun=rdo_horizon_plugins_tr),
    # XStatic projects (name is python-pypi_name, no lowercase conversion)
    RegexRule(pattern=r'^XStatic.*', pkgfun=rdo_xstatic_tr),
    # Tempest plugins (normalized to python-<project>-tests-tempest)
    RegexRule(pattern=r'\w+-tempest-plugin', pkgfun=rdo_tempest_plugins_tr)
]


SUSE_PKG_MAP = [
    # not following SUSE naming policy
    MultiRule(
        mods=['ansible',
              'libvirt-python',
              'python-ldap'],
        pkgfun=same_name_python3_prefix),
    # OpenStack services
    MultiRule(
        # keep lists in alphabetic order
        mods=['ceilometer', 'cinder', 'designate', 'glance',
              'heat', 'ironic', 'karbor', 'keystone', 'manila', 'masakari',
              'masakari-monitors', 'mistral',
              'monasca-agent', 'monasca-api', 'monasca-ceilometer',
              'monasca-log-api', 'monasca-notification', 'monasca-persister',
              'monasca-transform', 'neutron', 'nova', 'rally', 'sahara',
              'swift', 'Tempest', 'trove', 'tuskar', 'zaqar'],
        pkgfun=openstack_prefix_tr),
    # OpenStack clients
    MultiRule(
        mods=['python-%sclient' % c for c in (
            'barbican', 'ceilometer', 'cinder', 'cloudkitty', 'congress',
            'cue', 'designate', 'distil', 'drac', 'fuel', 'freezer', 'heat',
            'glance', 'glare', 'ironic', 'ironic-inspector-',
            'karbor', 'k8s', 'keystone',
            'magnum', 'manila', 'masakari', 'mistral', 'monasca',
            'murano', 'nimble', 'neutron', 'nova', 'oneview',
            'openstack', 'sahara', 'scci', 'searchlight',
            'senlin', 'smaug', 'solum', 'swift', 'tacker',
            'tripleo', 'trove', 'vitrage', 'watcher', 'zaqar')],
        pkgfun=subst_python2_python3),
    SingleRule('devel', 'python-devel', 'python3-devel'),
    # ui components
    SingleRule('horizon', 'openstack-dashboard'),
    SingleRule('designate-dashboard', 'openstack-horizon-plugin-designate-ui'),
    SingleRule('group-based-policy-ui', 'openstack-horizon-plugin-gbp-ui'),
    SingleRule('ironic-ui', 'openstack-horizon-plugin-ironic-ui'),
    SingleRule('magnum-ui', 'openstack-horizon-plugin-magnum-ui'),
    SingleRule('manila-ui', 'openstack-horizon-plugin-manila-ui'),
    SingleRule('monasca-ui', 'openstack-horizon-plugin-monasca-ui'),
    SingleRule('murano-dashboard', 'openstack-horizon-plugin-murano-ui'),
    SingleRule('neutron-fwaas-dashboard',
               'openstack-horizon-plugin-neutron-fwaas-ui'),
    SingleRule('neutron-lbaas-dashboard',
               'openstack-horizon-plugin-neutron-lbaas-ui'),
    SingleRule('neutron-vpnaas-dashboard',
               'openstack-horizon-plugin-neutron-vpnaas-ui'),
    SingleRule('sahara-dashboard', 'openstack-horizon-plugin-sahara-ui'),
    SingleRule('trove-dashboard', 'openstack-horizon-plugin-trove-ui'),
    SingleRule('networking-vsphere', 'openstack-neutron-vsphere'),
]

UBUNTU_PKG_MAP = [
    SingleRule('django_openstack_auth', 'python-openstack-auth'),
    SingleRule('glance_store', 'python-glance-store'),
    SingleRule('GitPython', 'python-git'),
    SingleRule('libvirt-python', 'python-libvirt'),
    SingleRule('PyMySQL', 'python-mysql'),
    SingleRule('pyOpenSSL', 'python-openssl'),
    SingleRule('PyYAML', 'python-yaml'),
    SingleRule('sqlalchemy-migrate', 'python-migrate'),
    SingleRule('suds-jurko', 'python-suds'),

    # Openstack clients
    MultiRule(
        mods=['python-%sclient' % c for c in (
            'barbican', 'ceilometer', 'cinder', 'cloudkitty', 'congress',
            'designate', 'fuel', 'heat', 'glance', 'ironic',
            'karbor',  'keystone',
            'magnum', 'manila', 'masakari', 'mistral', 'monasca',
            'murano', 'neutron', 'nova',
            'openstack', 'sahara',
            'senlin', 'swift',
            'trove',  'zaqar')],
        pkgfun=same_name_python_subst_python3),

]

OPENSTACK_UPSTREAM_PKG_MAP = [
    SingleRule('openstacksdk', 'python-openstacksdk'),
    SingleRule('gnocchiclient', 'python-gnocchiclient'),
    SingleRule('aodhclient', 'python-aodhclient'),
    SingleRule('keystoneauth1', 'keystoneauth'),
    SingleRule('microversion_parse', 'microversion-parse'),
    SingleRule('XStatic-smart-table', 'xstatic-angular-smart-table'),
]


def get_pkg_map(dist):
    if dist.lower().find('suse') != -1:
        return SUSE_PKG_MAP
    if dist.lower().find('ubuntu') != -1:
        return UBUNTU_PKG_MAP
    return RDO_PKG_MAP


def get_default_tr_func(dist):
    if dist.lower().find('suse') != -1:
        return default_suse_tr
    if dist.lower().find('ubuntu') != -1:
        return default_ubuntu_tr
    return default_rdo_tr


def module2package(mod, dist, pkg_map=None, py_vers=('py2',)):
    """Return a corresponding package name for a python module.

    mod  -- python module name
    dist -- a linux distribution as returned by
            `platform.linux_distribution()[0]`
    """
    if not pkg_map:
        pkg_map = get_pkg_map(dist)
    for rule in pkg_map:
        pkglist = rule(mod, dist)
        if pkglist:
            break
    else:
        tr_func = get_default_tr_func(dist)
        pkglist = tr_func(mod)

    if len(py_vers) == 1:
        # A single item requested. Not returning a list to keep
        # backwards compatibility
        if 'py2' in py_vers:
            return pkglist[0]
        elif 'py3' in py_vers:
            return pkglist[1]
    else:
        output = []
        if 'py2' in py_vers:
            output.append(pkglist[0])
        if 'py3' in py_vers:
            output.append(pkglist[1])
        return output


def module2upstream(mod):
    """Return a corresponding OpenStack upstream name for a python module.

    mod  -- python module name
    """
    for rule in OPENSTACK_UPSTREAM_PKG_MAP:
        pkglist = rule(mod, dist=None)
        if pkglist:
            return pkglist[0]
    return mod


def main():
    """for resolving names from command line"""
    parser = argparse.ArgumentParser(description='Python module name to'
                                     'package name')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--dist', help='distribution style '
                       '(default: %(default)s)',
                       default=platform.linux_distribution()[0])
    group.add_argument('--upstream', help='map to OpenStack project name',
                       action='store_true')
    parser.add_argument('--pyver', help='Python versions to return',
                        action='append', choices=['py2', 'py3'], default=[])
    parser.add_argument('modulename', help='python module name')
    args = vars(parser.parse_args())

    pyversions = args['pyver'] if args['pyver'] else ['py2']

    if args['upstream']:
        print(module2upstream(args['modulename']))
    else:
        pylist = module2package(args['modulename'], args['dist'],
                                py_vers=pyversions)
        # When only 1 version is requested, it will be returned as a string,
        # for backwards compatibility. Else, it will be a list.
        if type(pylist) is list:
            print(' '.join(pylist))
        else:
            print(pylist)


# for debugging to call the file directly
if __name__ == "__main__":
    main()
