'''Test configuration for the re-write unit tests'''

import pytest

from pymco.test import ctxt
from pymco.test import utils
from pymco.test.utils import mock

CONFIGSTR = '''
topicprefix = /topic/
collectives = mcollective,sub1,sub2
main_collective = mcollective
libdir = /path/to/plugins
logfile = /path/to/mcollective.log
loglevel = debug
daemonize = 0
identity = mco1

# Plugins
securityprovider = ssl
plugin.ssl_server_public = /path/to/server-public.pem
plugin.ssl_client_private = /path/to/client-private.pem
plugin.ssl_serializer = yaml
plugin.ssl_client_public = /path/to/client-public.pem

direct_addressing = yes
direct_addressing_threshold = 5

connector = activemq
plugin.activemq.pool.size = 2
plugin.activemq.pool.1.port = 6163
plugin.activemq.pool.1.host = localhost
plugin.activemq.pool.1.password = secret
plugin.activemq.pool.1.user = mcollective
plugin.activemq.pool.1.ssl = true
plugin.activemq.pool.1.ssl.ca = tests/fixtures/ca.pem
plugin.activemq.pool.1.ssl.key = tests/fixtures/activemq_private.pem
plugin.activemq.pool.1.ssl.cert = tests/fixtures/activemq_cert.pem
plugin.activemq.pool.2.port = 6164
plugin.activemq.pool.2.host = localhost
plugin.activemq.pool.2.password = secret
plugin.activemq.pool.2.user = mcollective
plugin.activemq.pool.2.ssl = true
plugin.activemq.pool.2.ssl.ca = tests/fixtures/ca.pem
plugin.activemq.pool.2.ssl.key = tests/fixtures/activemq_private.pem
plugin.activemq.pool.2.ssl.cert = tests/fixtures/activemq_cert.pem

factsource = yaml
plugin.yaml = /path/to/facts.yaml
'''


def pytest_runtest_setup(item):
    utils.configfile()


@pytest.fixture
def configstr():
    return CONFIGSTR


@pytest.fixture
def config(configstr):
    # Importing here since py-cov will ignore code imported on conftest files
    # imports
    from pymco import config
    return config.Config.from_configstr(configstr=configstr)


@pytest.fixture
def filter_():
    '''Creates a new :py:class:`pymco.message.Filter` instance.'''
    # Importing here since py-cov will ignore code imported on conftest files
    # imports
    from pymco import message
    return message.Filter()


@pytest.fixture
def msg(config, filter_):
    '''Creates a new :py:class:`pymco.message.Message` instance.'''
    # Importing here since py-cov will ignore code imported on conftest files
    # imports
    from pymco import message
    with mock.patch('time.time') as time:
        with mock.patch('hashlib.sha1') as sha1:
            time.return_value = ctxt.MSG['msgtime']
            sha1.return_value.hexdigest.return_value = ctxt.MSG['requestid']
            msg_ = message.Message(body=ctxt.MSG['body'],
                                   agent=ctxt.MSG['agent'],
                                   filter_=filter_,
                                   config=config)
            time.assert_called_once_with()
            sha1.return_value.hexdigest.assert_called_once_with()
    return msg_


@pytest.fixture
def msg_with_data(config, filter_):
    """Creates :py:class:`pymco.message.Message` instance with some data."""
    # Importing here since py-cov will ignore code imported on conftest files
    # imports
    from pymco import message
    with mock.patch('time.time') as time:
        with mock.patch('hashlib.sha1') as sha1:
            time.return_value = ctxt.MSG['msgtime']
            sha1.return_value.hexdigest.return_value = ctxt.MSG['requestid']
            body = {
                ':action': 'runonce',
                ':data': {':noop': True, ':process_results': True},
                ':ssl_msgtime': 1421878604,
                ':ssl_ttl': 60,
            }
            return message.Message(body=body,
                                   agent='puppet',
                                   filter_=filter_,
                                   config=config)


@pytest.fixture
def security():
    return mock.Mock()

conn_mock = security
