"""
:py:mod:`pymco.message`
-----------------------
python-mcollective messaging objects.
"""
import collections
import hashlib
import time

import six

from . import exc


class Filter(collections.Mapping):
    """Provides MCollective filters for python-mcollective.

    This class implements :py:class:`collections.Mapping` interface, so it can
    be used as non mutable mapping (read only dict), but mutable using provided
    add methods. So that, for adding the agent you can just use
    :py:meth:`add_agent`::

        filter.add_agent('package')
    """
    def __init__(self):
        self._filter = {
            'cf_class': [],
            'agent': [],
            'fact': [],
            'identity': [],
            'compound': [],
        }

    def add_cfclass(self, name):
        """Add new class applied by your configuration management system.

        Roles, cookbooks,... names may be used too.

        Args:
            ``name``: class, role, cookbook,... name.

        Returns:
            ``self``: so filters can be chained.
        """
        self._filter['cf_class'].append(name)
        return self

    def add_agent(self, agent):
        """Add new MCollective agent

        Args:
            ``agent``: MCollective agent name.

        Returns:
            ``self``: so filters can be chained.
        """
        self._filter['agent'].append(agent)
        return self

    def add_fact(self, fact, value, operator=None):
        """Add a new Facter fact based filter.

        Args:
            ``fact``: fact name.

            ``value``: fact value.

            ``operator``: Operator to be applied when comparing the fact. Valid
            values are: ==, <=, >=, <, >, !=.

        Returns:
            ``self``: so filters can be chained.
        """
        toappend = {':fact': fact, ':value': value}
        if operator:
            if not operator in ('==', '<=', '>=', '<', '>', '!='):
                raise exc.BadFilterFactOperator(
                    'Unsuppoerted operator {0}'.format(operator))
            toappend[':operator'] = operator
        self._filter['fact'].append(toappend)
        return self

    def add_identity(self, identity):
        """Adds new identities

        Args:
            ``identity``: MCollective identity value.

        Returns:
            ``self``: so filters can be chained.
        """
        self._filter['identity'].append(identity)
        return self

    def __getitem__(self, key):
        return self._filter[key]

    def __len__(self):
        return len(self._filter)

    def __iter__(self):
        return six.iterkeys(self._filter)


class Message(collections.MutableMapping):
    """Provides MCollective messages for python-mcollective.

    This class implements :py:class:`collections.MutableMapping` interface, so
    it can be used as read/write mapping (dictionary).
    """
    def __init__(self, body, agent, config, filter_=None, **kwargs):
        if not filter_:
            filter_ = Filter()

        self._message = {}
        try:
            self._message[':senderid'] = config['identity']
            self._message[':collective'] = (kwargs.get('collective', None) or
                                            config['main_collective'])
        except KeyError as error:
            raise exc.ImproperlyConfigured(error)
        self._message[':msgtime'] = int(time.time())
        self._message[':ttl'] = (kwargs.get('ttl', None) or
                                 config.getint('ttl', default=60))
        self._message[':requestid'] = hashlib.sha1(
            str(self._message[':msgtime']).encode('utf-8')).hexdigest()
        self._message[':body'] = body
        self._message[':agent'] = agent
        self._message[':filter'] = dict(filter_)

    def __len__(self):
        return len(self._message)

    def __iter__(self):
        return six.iterkeys(self._message)

    def __getitem__(self, key):
        return self._message[key]

    def __setitem__(self, key, value):
        if not key.startswith(':'):
            raise ValueError('Keys must start with `:`, as Ruby symbols.')

        if key == ':filter':
            value = dict(value)
        self._message[key] = value

    def __delitem__(self, key):
        del self._message[key]
