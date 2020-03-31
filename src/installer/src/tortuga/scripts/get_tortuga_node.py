# Copyright 2008-2018 Univa Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os.path
import sys
import yaml

from tortuga.config.configManager import ConfigManager
from tortuga.db.dbManager import DbManager
from tortuga.db.globalParametersDbHandler import GlobalParametersDbHandler
from tortuga.db.helper import get_installer_hostname_suffix
from tortuga.db.nodesDbHandler import NodesDbHandler
from tortuga.exceptions.nodeNotFound import NodeNotFound
from tortuga.exceptions.parameterNotFound import ParameterNotFound
from tortuga.kit.loader import load_kits
from tortuga.kit.registry import get_kit_installer
from tortuga.logging import PUPPET_NAMESPACE


logger = logging.getLogger(PUPPET_NAMESPACE)

dbm = DbManager()

def flatten_one_level(classes: dict):
    new_classes = {}
    for key, value in classes.items():
        # if value is a not-empty dictonary, flatten first level
        if isinstance(value, dict) and value:
            for key2, value2 in value.items():
                new_classes["%s::%s" % (key,key2)] = value2
        else:
            new_classes[key] = value
    return new_classes

def main():
    if len(sys.argv) != 2:
        sys.exit(1)

    # ensure all available kits are loaded
    load_kits()

    nodeName = sys.argv[1].lower()

    # Load DNSZone from GlobalParameters
    session = dbm.openSession()

    try:
        get_puppet_node_yaml(session, nodeName)
    finally:
        dbm.closeSession()


def get_puppet_node_yaml(session, nodeName):
    _cm = ConfigManager()

    publicInstallerFQDN = _cm.getInstaller().lower()
    primaryInstallerHostName = publicInstallerFQDN.split('.', 1)[0]

    try:
        dnsZone = GlobalParametersDbHandler().getParameter(
            session, 'DNSZone').value.lower()
    except ParameterNotFound:
        dnsZone = None

    try:
        depot_path = GlobalParametersDbHandler().getParameter(
            session, 'depot').value.lower()

        _cm.setDepotDir(depot_path)
    except ParameterNotFound:
        pass

    bInstaller = primaryInstallerHostName == nodeName.split('.', 1)[0]

    try:
        dbNode = NodesDbHandler().getNode(session, nodeName)
    except NodeNotFound:
        sys.exit(1)

    data = None
    try:
        from tortuga.db.dataRequestsDbHandler import DataRequestsDbHandler
        dbDataRequest = DataRequestsDbHandler().get_by_addHostSession(session, dbNode.addHostSession)
        if dbDataRequest:
            data = dbDataRequest.request
    except Exception as e:
        pass

    if dbNode.hardwareprofile.nics:
        privateInstallerFQDN = '%s%s%s' % (
            primaryInstallerHostName,
            get_installer_hostname_suffix(
                dbNode.hardwareprofile.nics[0], enable_interface_aliases=None),
            '.%s' % (dnsZone) if dnsZone else '')
    else:
        privateInstallerFQDN = '%s%s' % (
            primaryInstallerHostName, '.%s' % (dnsZone) if dnsZone else '')

    if not bInstaller and dbNode.hardwareprofile.location == 'local':
        # If the hardware profile does not have an associated provisioning
        # NIC, use the public installer FQDN by default. This can happen if
        # the user has added their own "public" nodes to a local hardware
        # profile.

        if not dbNode.hardwareprofile.nics:
            installerHostName = publicInstallerFQDN
        else:
            installerHostName = privateInstallerFQDN
    else:
        # If the specified node is the installer itself or a node
        # accessing the installer through it's public interface, use the
        # public host name.
        installerHostName = publicInstallerFQDN

    puppet_classes = {}

    enabledKits = set()

    if dbNode.softwareprofile:

        for dbComponent in dbNode.softwareprofile.components:

            if not dbComponent.kit.isOs:
                #
                # Load the kit and component installers
                #
                kit_spec = (
                    dbComponent.kit.name,
                    dbComponent.kit.version,
                    dbComponent.kit.iteration
                )
                kit_installer = get_kit_installer(kit_spec)()
                kit_installer.session = session
                _component = kit_installer.get_component_installer(
                    dbComponent.name)

                #
                # Get the puppet args for the component
                #
                try:
                    puppet_class_args = _component.run_action(
                        'get_puppet_args',
                        dbNode.softwareprofile,
                        dbNode.hardwareprofile,
                        data = data
                    )
                    if puppet_class_args is not None:
                        puppet_classes[_component.puppet_class] = \
                            puppet_class_args
                except Exception as e:  # noqa pylint: disable=broad-except
                    # display exception message in puppet output
                    msg = '{}: {}'.format(_component.puppet_class, e)
                    if not puppet_classes.get('tortuga_kit_base::common::message'):
                        puppet_classes['tortuga_kit_base::common::message'] = { 'msg' : [ msg ] }
                    else:
                        puppet_classes['tortuga_kit_base::common::message']['msg'].append(msg)
                     # suppress exception if unable to get Puppet args
                    puppet_classes[_component.puppet_class] = {}

            else:
                #
                # OS kit component is omitted on installer. The installer
                # is assumed to have a pre-existing OS repository
                # configuration.
                #
                if bInstaller:
                    continue

            enabledKits.add(dbComponent.kit)

    dataDict = {}
    if puppet_classes:
        dataDict['classes'] = [ *puppet_classes ]

    # flatten = True
    # if flatten:
    #     dataDict['classes'] = [ *puppet_classes ]
    #     parametersDict = flatten_one_level(puppet_classes)
    # else:
    #     dataDict['classes'] = puppet_classes
    #     parametersDict = {}

    parametersDict = flatten_one_level(puppet_classes)
    dataDict['parameters'] = parametersDict

    # software profile
    if dbNode.softwareprofile:
        parametersDict['swprofilename'] = dbNode.softwareprofile.name

    # hardware profile
    parametersDict['hwprofilename'] = dbNode.hardwareprofile.name

    # installer hostname
    parametersDict['primary_installer_hostname'] = installerHostName

    # Local repos directory
    repodir = os.path.join(_cm.getDepotDir(), 'kits')

    # Build YUM repository entries only if we have kits associated with
    # the software profile.
    if enabledKits:
        repourl = _cm.getIntWebRootUrl(installerHostName) + '/repos' \
            if not bInstaller else 'file://{0}'.format(repodir)

        repo_type = None

        if dbNode.softwareprofile.os.family.name == 'rhel':
            repo_type = 'yum'
        # elif dbNode.softwareprofile.os.family == 'ubuntu':
        #     repo_type = 'apt'

        if repo_type:
            # Only add 'repos' entries for supported operating system
            # families.

            repos_dict = {}

            for kit in enabledKits:
                if kit.isOs:
                    verstr = str(kit.version)
                    arch = kit.components[0].os[0].arch
                else:
                    verstr = '%s-%s' % (kit.version, kit.iteration)
                    arch = 'noarch'

                for dbKitSource in dbNode.softwareprofile.kitsources:
                    if dbKitSource in kit.sources:
                        baseurl = dbKitSource.url
                        break
                else:
                    subpath = '%s/%s/%s' % (kit.name, verstr, arch)

                    if not kit.isOs and not os.path.exists(
                            os.path.join(repodir,
                                         subpath,
                                         'repodata/repomd.xml')):
                        continue

                    baseurl = '%s/%s' % (repourl, subpath)

                    # [TODO] temporary workaround for handling RHEL media
                    # path.
                    #
                    # This code is duplicated from tortuga.boot.distro
                    if kit.isOs and \
                       dbNode.softwareprofile.os.name == 'rhel' and \
                       dbNode.softwareprofile.os.family.version != '7':
                        subpath += '/Server'

                if repo_type == 'yum':
                    if dbNode.hardwareprofile.location == 'remote':
                        cost = 1200
                    else:
                        cost = 1000

                    repos_dict['uc-kit-%s' % (kit.name)] = {
                        'type': repo_type,
                        'baseurl': baseurl,
                        'cost': cost,
                    }

            if repos_dict:
                parametersDict['repos'] = repos_dict

    # Enable '3rdparty' repo
    if dbNode.softwareprofile:
        third_party_repo_subpath = '3rdparty/%s/%s/%s' % (
            dbNode.softwareprofile.os.family.name,
            dbNode.softwareprofile.os.family.version,
            dbNode.softwareprofile.os.arch)

        local_repos_path = os.path.join(repodir, third_party_repo_subpath)

        # Check for existence of repository metadata to validate existence
        if enabledKits and os.path.exists(
                os.path.join(local_repos_path, 'repodata', 'repomd.xml')):
            third_party_repo_dict = {
                'tortuga-third-party': {
                    'type': 'yum',
                    'baseurl': os.path.join(repourl, third_party_repo_subpath),
                },
            }

            if 'repos' not in parametersDict:
                parametersDict['repos'] = third_party_repo_dict
            else:
                parametersDict['repos'] = dict(
                    list(parametersDict['repos'].items()) +
                    list(third_party_repo_dict.items()))

    # environment
    dataDict['environment'] = 'production'

    sys.stdout.write(
        yaml.safe_dump(
            dataDict, default_flow_style=False, explicit_start=True))
