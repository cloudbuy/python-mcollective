"""Tests YAML serializer"""
import mock

from pymco.serializers import yaml as _yaml


def test_serialize(yaml, msg):
    """Test msg serialization"""
    assert yaml.serialize(msg) == """:agent: discovery
:body: ping
:collective: mcollective
:filter:
  agent: []
  cf_class: []
  compound: []
  fact: []
  identity: []
:msgtime: 123
:requestid: 6ef11a5053008b54c03ca934972fdfa45448439d
:senderid: mco1
:ttl: 60
"""


def test_serialize_data(yaml, msg_with_data):
    assert yaml.serialize(msg_with_data) == """:agent: puppet
:body:
  :action: runonce
  :data:
    :noop: true
    :process_results: true
  :ssl_msgtime: 1421878604
  :ssl_ttl: 60
:collective: mcollective
:filter:
  agent: []
  cf_class: []
  compound: []
  fact: []
  identity: []
:msgtime: 123
:requestid: 6ef11a5053008b54c03ca934972fdfa45448439d
:senderid: mco1
:ttl: 60
"""


def test_deserialize(yaml, yaml_response):
    assert yaml.deserialize(yaml_response) == {
        ':senderid': 'mco1',
        ':requestid': '335a3e8261e4589499d366862b328816',
        ':senderagent': 'discovery',
        ':msgtime': 1384022186,
        ':body': 'pong',
    }


def test_symbol_constructor():
    loader, node = mock.Mock(), mock.Mock(value='foo')
    assert _yaml.symbol_constructor(loader, node) == ':foo'


def test_ruby_object_constructor():
    loader, node = mock.Mock(), mock.Mock()
    assert _yaml.ruby_object_constructor(
        loader, 'Puppet:Resuource', node
    ) == loader.construct_yaml_map.return_value
    loader.construct_yaml_map.assert_called_once_with(node)
