"""
Serializers
-----------------------
Provides Marshal [de]serialization.
"""

import collections
import logging

from . import SerializerBase

from rubymarshal.reader import loads as _loads
from rubymarshal.writer import writes as _writes
from rubymarshal.classes import Symbol


def convert_string_to_symbols(msg):
    msg_dict = {}
    for key, value in msg.items():
        if key.startswith(':'):
            key = Symbol(key[1:])
        if isinstance(value, dict):
            value = convert_string_to_symbols(value)
        msg_dict[key] = value
    return msg_dict


def convert_symbols_to_strings(msg):
    msg_dict = {}
    for key, value in msg.items():
        if isinstance(key, Symbol):
            key = ':' + key.name
        if isinstance(value, dict):
            value = convert_symbols_to_strings(value)
        msg_dict[key] = value
    return msg_dict


def loads(obj):
    obj = _loads(obj)
    if isinstance(obj, (collections.Mapping, dict)):
        obj = convert_symbols_to_strings(obj)
    return obj


def writes(obj):
    if isinstance(obj, (collections.Mapping, dict)):
        obj = convert_string_to_symbols(obj)
    return _writes(obj)


class Serializer(SerializerBase):

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def serialize(self, msg):
        self.logger.debug("serializing with Marshal")
        self.logger.debug('%r', dict(msg))
        return writes(msg)

    def deserialize(self, msg):
        self.logger.debug("deserializing with Marshal")
        return loads(msg)
