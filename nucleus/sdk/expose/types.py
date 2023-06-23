from __future__ import annotations

from jwcrypto import jwe, jwk, jws

from nucleus.core.types import Literal, Protocol, Raw, Setting, Union
from nucleus.sdk.storage import Object, Store

JWK = jwk.JWK
JWS = jws.JWS
JWE = jwe.JWE

Claims = Literal['s', 'd', 't']
JWT = Union[JWS, JWE]


class Metadata(Protocol):
    """Metadata defines the expected behavior of metadata types.
    Examples of metadata types include:

    - Descriptive
    - Structural
    - Technical

    """

    def __str__(self) -> Claims:
        """Metadata types MUST return the specified claims as a string.
        Examples of valid claims include: s, t, d
        """
        ...


class Standard(Protocol):
    """Standard defines the expected behavior of Standard implementations.
    ref: https://github.com/SynapseMedia/sep/blob/main/SEP/SEP-001.md
    """

    def header(self) -> Raw:
        """Return the standard header"""
        ...

    def payload(self) -> Raw:
        """Return the standard payload"""
        ...


class Serializer(Protocol):
    """Serializer observer specifies the methods needed to handle SEP001 serialization.
    Defines how to handle serialization for each strategy according to the specification, which includes:

    - Compact
    - DAG-JOSE

    This template class must be implemented by other classes that provide concrete serialization logic.
    ref: https://github.com/SynapseMedia/sep/blob/main/SEP/SEP-001.md
    """

    def __str__(self) -> str:
        """The serialized data as string
        
        :return: 
        """
        ...

    def __bytes__(self) -> bytes:
        """The payload data ready to sign/encrypt
        
        :return:
        """
        ...

    def __iter__(self) -> Setting:
        """Yield `typ` headers specified in RFC 7517/7516 standard.
        
        :return: The iterable media type settings
        """
        ...

    def __init__(self, standard: Standard):
        """Serializer must be initialized with Standard implementation
        
        :param standard: The standard implementation
        """
        ...

    def save_to(self, store: Store) -> Object:
        """Could be used to store assets.
        eg. After generate CID from payload dag-cbor we need to store the bytes into blocks
        
        :param store: The local store function
        :return: Object instance
        """

        ...

    def update(self, jwt: JWT) -> Serializer:
        """Receive updates when serialization is ready to handle any additional encoding step.
        In this step we could add a new state or operate over JWS/JWE to handle any additional encoding.

        :param jwt: The type of JWT implementation to handle
        :return: Self serializer
        """
        ...


class Keyring(Protocol):
    """Keyring specifies the required methods for handling
    keys based on the JWK (JSON Web Key) RFC 7517 standard.
    """

    def __iter__(self) -> Setting:
        """Yield `alg` and `jwk` headers specified in RFC 7517/7516 standard.
        
        :return: The iterable header settings to associate
        """
        ...

    def jwk(self) -> JWK:
        """Return the internal JWK (JSON Web Key) instance
        
        :return: The JWK (JSON Web Key) instance
        """
        ...

    def fingerprint(self) -> str:
        """Return the base64 decoded thumbprint as specified by RFC 7638
        
        :return: The decoded thumbprint as string. eg: sha256, blake, etc..
        
        """
        ...

    def from_dict(self, raw_key: Raw) -> Keyring:
        """Initialize Keyring using JWK JSON format
        
        :param raw_key: Keyring to import as dict (JSON format)
        :return: KeyRing object
        """
        ...

    def as_dict(self) -> Raw:
        """Export Keyring as JWK JSON format
        
        :return: Keyring as dict
        """
        ...


class Crypto(Protocol):
    """Specify a pub/sub middleware that handle cryptographic operations on serializers."""

    def __init__(self, serializer: Serializer):
        """Initialize with the serializer on which we will operate.
        
        :param serializer: The serializer implementation
        """
        ...

    def serialize(self) -> Serializer:
        """Notify the underlying serializer of the current state of the cryptographic operation.
        During this process, the serializer may modify its state or store the results of the operations.
        
        :return: The input Serializer with a new ready to use state
        """
        ...

    def add_key(self, kr: Keyring) -> Crypto:
        """Bind keys to the serialization process.

        :param kr: Keyring to associate with operation
        :return: Crypto object
        """
        ...


__all__ = ()
