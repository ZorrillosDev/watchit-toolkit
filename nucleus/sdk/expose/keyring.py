from __future__ import annotations

import jwt

# ref: https://cryptography.io/en/latest/hazmat/primitives/asymmetric/ec/
import cryptography.hazmat.primitives.serialization as serialization
import cryptography.hazmat.primitives.asymmetric.ec as ec

from nucleus.core.types import Raw, Any
from dataclasses import dataclass
from enum import Enum


class Algorithm(str, Enum):
    ES256 = "ES256"
    ES256K = "ES256K"  # ECDSA + secp256k1


class KeyType(str, Enum):
    EllipticCurve = "EC"
    RSA = "RSA"


class Curve(str, Enum):
    P256 = "P256"
    ED25519 = "ED25519"
    Secp256k1 = "Secp256k1"


@dataclass(slots=True)
class KeyRing:
    algorithm: Algorithm
    key_type: KeyType
    curve: Curve

    def get_key(self) -> KeyRing:
        return self._key

    def generate_keys(self) -> KeyRing:
        curve = ec.SECP256K1()
        private = ec.generate_private_key(curve)
        public = private.public_key()
        return KeyRing(private, public)

    def sign(self, raw: str, **kwargs: Any) -> bytes:
        ...

    def verify(self, sig: str, **kwargs: Any) -> bool:
        try:
            public_pem = self._key.public_pem().decode()
            jwt.decode(sig, public_pem, **kwargs)  # type: ignore
            return True
        except jwt.DecodeError as error:
            raise error


__all__ = ("Algorithm", "KeyType", "Curve", "KeyRing")
