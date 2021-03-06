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

from tortuga.exceptions.tortugaException import TortugaException
from .tortugaWsApi import TortugaWsApi


class ResourceAdapterConfigurationWsApi:
    """
    Resource adapter configuration client web service API

    """
    def __init__(self, *args, **kwargs):
        self._client = TortugaWsApi(*args, **kwargs)

    def create(self, resadapter_name, name, configuration):
        url = 'resourceadapters/{0}/profile/{1}'.format(
            resadapter_name, name)

        postdata = dict(configuration=configuration)

        try:
            responseDict = self._client.post(url, postdata)

            return responseDict

        except TortugaException:
            raise

        except Exception as ex:
            raise TortugaException(exception=ex)

    def get(self, resadapter_name, name):
        """Get resource adapter configuration"""

        url = 'resourceadapters/{0}/profile/{1}'.format(
            resadapter_name, name)

        try:
            responseDict = self._client.get(url)

            return responseDict

        except TortugaException:
            raise

        except Exception as ex:
            raise TortugaException(exception=ex)

    def validate(self, resadapter_name: str, name: str):
        """
        Validate resource adapter configuration

        :param str resadapter_name: the name of the resource adapter
        :param str name:            the name of the configuration profile

        """

        url = 'resourceadapters/{}/profile/{}/validate'.format(
            resadapter_name, name)

        try:
            responseDict = self._client.get(url)

            return responseDict

        except TortugaException:
            raise

        except Exception as ex:
            raise TortugaException(exception=ex)

    def get_profile_names(self, resadapter_name):
        url = 'resourceadapters/{0}/profile/'.format(resadapter_name)

        try:
            responseDict = self._client.get(url)

            return responseDict

        except TortugaException:
            raise

        except Exception as ex:
            raise TortugaException(exception=ex)

    def delete(self, resadapter_name, name):
        url = 'resourceadapters/{0}/profile/{1}'.format(
            resadapter_name, name)

        try:
            responseDict = self._client.delete(url)

            return responseDict

        except TortugaException:
            raise

        except Exception as ex:
            raise TortugaException(exception=ex)

    def update(self, resadapter_name, name, configuration):
        url = 'resourceadapters/{0}/profile/{1}'.format(
            resadapter_name, name)

        try:
            responseDict = self._client.put(url, configuration)

            return responseDict

        except TortugaException:
            raise

        except Exception as ex:
            raise TortugaException(exception=ex)
