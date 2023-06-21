from __future__ import annotations

from dataclasses import dataclass, field

from nucleus.core.types import CID, List, Optional, Raw, Type

from .crypto import Sign
from .marshall import DagJose
from .types import Crypto, Keyring, Metadata, Serializer

"""Standard implementation for SEP-001 .
ref: https://github.com/SynapseMedia/sep/blob/main/SEP/SEP-001.mdhttps://github.com/SynapseMedia/sep/blob/main/SEP/SEP-001.md
"""


@dataclass
class Header:
    """JWT Header standard based on SEP-001:
    ref: https://github.com/SynapseMedia/sep/blob/main/SEP/SEP-001.md
    """

    # Is used by JWT applications to declare the media type [IANA.MediaTypes]
    # of this complete JWT
    typ: str


@dataclass(init=False)
class Payload:
    """JWT Payload standard based on SEP-001:
    ref: https://github.com/SynapseMedia/sep/blob/main/SEP/SEP-001.md
    """

    s: Raw  # s: structural metadata Object
    d: Raw  # d: descriptive metadata Object
    t: Optional[Raw] = None  # t: technical metadata Object
    r: Optional[CID] = None  # r: reserved for future use

    def add(self, meta: Metadata) -> None:
        """Associate metadata to payload.

        :param meta: The metadata type to store in payload
        :raises NotImplementedError: If invalid metadata is added
        """
        setattr(self, str(meta), vars(meta))


@dataclass(slots=True)
class SEP001:
    """SEP-001 standard implementation:
    ref: https://github.com/SynapseMedia/sep/blob/main/SEP/SEP-001.md
    """

    _header: Header
    _payload: Payload

    _keys: List[Keyring] = field(init=False)
    # serialization method eg. DagJose, Compact, etc
    _method: Type[Serializer] = field(init=False)
    # crypto operation type eg. Sign, Cypher
    _crypto: Type[Crypto] = field(init=False)

    def __post_init__(self):
        self._keys = []
        self._method = DagJose  # default
        self._crypto = Sign  # default

    def header(self) -> Raw:
        return vars(self._header)

    def payload(self) -> Raw:
        return vars(self._payload)

    def add_key(self, kr: Keyring) -> None:
        """Add signature/recipient key.
        We use the keys later in the serialization process.

        :param kr: Key ring implementation
        :return: None
        """
        self._keys.append(kr)

    def add_metadata(self, meta: Metadata) -> None:
        """Add metadata to payload

        :param meta: The metadata type to store in payload
        :return: None
        """
        self._payload.add(meta)

    def set_operation(self, crypto: Type[Crypto]) -> None:
        """Set cryptography operation type to use during serialization.

        :param crypto: The crypto operation type
        :return: None
        """
        self._crypto = crypto

    def set_serialization(self, method: Type[Serializer]) -> None:
        """Set the serialization method.

        :param method: The serialization method
        :return: None
        """
        self._method = method

    def serialize(self) -> Serializer:
        """Serialize the standard according to the defined serialization method and crypto operation.

        :return: the out-of-the-box/ready-state serializer
        """
        serializer = self._method(self)
        crypto = self._crypto(serializer)

        # associate keys
        for k in self._keys:
            crypto.add_key(k)

        return crypto.serialize()


__all__ = ('SEP001', 'Header', 'Payload')