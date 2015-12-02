"""
:py:mod:`pymco.security.psk`
-------------------
Contains pre-shared key security provider plugin.
"""

import grp
import hashlib
import logging
import os
import platform

from . import SecurityProvider
from .. import exc
from .. serializers.marshal import Serializer, writes, loads


LOG = logging.getLogger(__name__)


class PSKProvider(SecurityProvider):

    serializer = Serializer()

    def __init__(self, config, logger=LOG):
        super(PSKProvider, self).__init__(config=config, logger=logger)
        self._preshared_key = config.get('plugin.psk').encode('utf-8')

    def get_hash(self, body):
        return hashlib.md5(body + self._preshared_key).hexdigest()

    def sign(self, msg):
        self.logger.debug("signing message using PSK provider")
        msg[':callerid'] = self.callerid
        msg[':body'] = writes(msg[':body'])
        msg[':hash'] = self.get_hash(msg[':body'])
        return msg

    def verify(self, msg):
        digest = self.get_hash(msg[':body'])
        if digest == msg[':hash']:
            msg[':body'] = loads(msg[':body'])
        else:
            self.logger.debug("message NOT verified")
            raise exc.VerificationError(
                'Message {0} can\'t be verified'.format(msg))
        return msg

    @property
    def callerid(self):
        """Property returning the mCollective PSK caller id.

        :return:
        """

        if 'plugin.psk.callertype' in self.config:
            caller_type = self.config['plugin.psk.callertype']
        else:
            caller_type = 'uid'

        if caller_type == 'gid':
            caller_id = 'gid={}'.format(os.getgid())
        elif caller_type == 'group':
            if platform.system() == 'Windows':
                raise exc.PyMcoException("Cannot use the 'group' callertype for the PSK security plugin on the Windows platform")
            caller_id = 'group={}'.format(grp.getgrnam(os.getgid()))
        elif caller_type == 'user':
            caller_id = 'user={}'.format(os.getlogin())
        elif caller_type == 'identity':
            caller_id = 'identity={}'.format(self.config.get('identity'))
        else:
            caller_id = 'uid={}'.format(os.getuid())

        self.logger.debug('Setting callerid to %s based on callertype=%s', caller_id, caller_type)
        return caller_id