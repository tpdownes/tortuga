#!/usr/bin/env python

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

# pylint: disable=no-member

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.exceptions.invalidCliRequest import InvalidCliRequest
from tortuga.wsapi.hardwareProfileWsApi import HardwareProfileWsApi


class DeleteHardwareProfileCli(TortugaCli):
    def __init__(self):
        super().__init__()

    def parseArgs(self, usage=None):
        option_group_name = _('Delete Hardware Profile Options')
        self.addOptionGroup(option_group_name, '')
        self.addOptionToGroup(option_group_name, '--name', required=True,
                              dest='hardwareProfileName',
                              help=_('Name of hardware profile to delete'))

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs(_('Removes hardware profile from the'))

        api = HardwareProfileWsApi(username=self.getUsername(),
                                   password=self.getPassword(),
                                   baseurl=self.getUrl())

        api.deleteHardwareProfile(
            self.getArgs().hardwareProfileName)


def main():
    DeleteHardwareProfileCli().run()
