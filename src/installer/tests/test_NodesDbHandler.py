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

import socket
import unittest

import pytest

from tortuga.db.models.node import Node
from tortuga.db.nodesDbHandler import NodesDbHandler
from tortuga.exceptions.nodeNotFound import NodeNotFound


@pytest.mark.usefixtures('dbm_class')
class TestNodesDbHandler(unittest.TestCase):
    def setUp(self):
        super(TestNodesDbHandler, self).setUp()

        self.session = self.dbm.openSession()

    def tearDown(self):
        # Perform session clean up before calling superclass
        self.dbm.closeSession()
        self.session = None

        super(TestNodesDbHandler, self).tearDown()

    def test_getNode(self):
        result = NodesDbHandler().getNode(self.session, socket.getfqdn())

        assert result.nics

    def test_getNodeList(self):
        assert isinstance(NodesDbHandler().getNodeList(self.session), list)

    def test_getNode_failed(self):
        with pytest.raises(NodeNotFound):
            NodesDbHandler().getNode(self.session, 'XXXXXXXX')

    def test_getNodeByIp(self):
        result = NodesDbHandler().getNodeByIp(self.session, '10.2.0.1')

        assert result.name == socket.getfqdn()

        assert result.nics

    def test_getNodesByTags(self):
        result = NodesDbHandler().getNodesByTags(
            self.session, [('tag1',)])

        assert match_all_nodes(result)

    def test_getNodesByTags_match_multiple(self):
        result = NodesDbHandler().getNodesByTags(
            self.session, [('tag1',), ('key2',)])

        assert match_all_nodes(result)

    def test_getNodesByTags_match_multiple_with_values(self):
        result = NodesDbHandler().getNodesByTags(
            self.session, [('tag1', 'value1'),
                           ('tag2', 'value2')])

        assert match_all_nodes(result)

    def test_getNodesByTags_nonexistent(self):
        result = NodesDbHandler().getNodesByTags(
            self.session, [('invalid_tag',)])

        assert not result

    def test_getNodesByTags_value_match(self):
        result = NodesDbHandler().getNodesByTags(
            self.session, [('tag1', 'value1')])

        assert match_all_nodes(result)

    def test_getNodesByTags_value_mismatch(self):
        result = NodesDbHandler().getNodesByTags(
            self.session, [('tag1', 'invalid_value',)])

        assert not result

    def test_getNodesByTags_one_match_one_nomatch(self):
        result = NodesDbHandler().getNodesByTags(
            self.session, [('tag1', 'value1'), ('nomatch',)])

        assert match_all_nodes(result)

    def test_getNodesByTag_non_contiguous(self):
        result = NodesDbHandler().getNodesByTags(
            self.session, [('tag5',)])

        assert not set(['compute-01.private',
                        'compute-02.private',
                        'compute-08.private']) - \
            set([node.name for node in result])


def match_all_nodes(result):
    # Match expected tags
    return not set(['compute-01.private',
                    'compute-02.private',
                    'compute-03.private',
                    'compute-04.private']) - \
        set([node.name for node in result])


if __name__ == '__main__':
    unittest.main()
