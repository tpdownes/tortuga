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

import datetime

from marshmallow import fields

from tortuga.types.base import BaseTypeSchema, BaseType


class CloudServerActionSchema(BaseTypeSchema):
    """
    Marshmallow schema for cloudserver actions.

    """
    action: fields.Field = fields.String()
    cloudserver_id: fields.Field = fields.String()
    cloudconnectorprofile_id: fields.Field = fields.String()
    timestamp: fields.Field = fields.DateTime()
    status: fields.Field = fields.String()
    status_message: fields.Field = fields.String()


class CloudServerAction(BaseType):
    """
    This is the cloudserver action type.

    """
    #
    # Requirements for BaseType
    #
    type = 'cloud-server-action'
    schema_class = CloudServerActionSchema

    STATUS_CREATED = "created"
    STATUS_PROCESSING = "processing"
    STATUS_COMPLETE = "complete"
    STATUS_ERROR = "error"

    def __init__(self, **kwargs):
        """
        Initialization.

        :param kwargs: any arguments provided will be assigned as attributes
                       directly on the instance.

        """
        super().__init__(**kwargs)
        self.action: str = kwargs.get('action', None)
        self.cloudserver_id: str = kwargs.get('cloudserver_id', None)
        self.cloudconnectorprofile_id: str = kwargs.get(
            'cloudconnectorprofile_id', None)
        self.timestamp: datetime.datetime = kwargs.get('timestamp', None)
        self.status: str = kwargs.get('status',
                                      CloudServerAction.STATUS_CREATED)
        self.status_message: str = kwargs.get('status_message', None)
