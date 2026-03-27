"""
Password hashing using PBKDF2-HMAC-SHA256 (Python stdlib — no extra dependency).

Each stored password is formatted as:  <salt_hex>:<hash_hex>
The salt is 16 random bytes, unique per password.
100 000 iterations make brute-force attacks expensive.
"""

import hashlib
import hmac
import os

_ITERATIONS = 100_000
_ALGORITHM  = "sha256"


def hash_password(password: str) -> str:
    """Return a salted hash string safe to store in the database."""
    salt = os.urandom(16)
    key  = hashlib.pbkdf2_hmac(_ALGORITHM, password.encode("utf-8"), salt, _ITERATIONS)
    return salt.hex() + ":" + key.hex()


def verify_password(password: str, stored: str) -> bool:
    """
    Return True if *password* matches the *stored* hash string.
    Uses hmac.compare_digest to prevent timing attacks.
    """
    try:
        salt_hex, key_hex = stored.split(":", 1)
        salt     = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(key_hex)
        actual   = hashlib.pbkdf2_hmac(_ALGORITHM, password.encode("utf-8"), salt, _ITERATIONS)
        return hmac.compare_digest(actual, expected)
    except (ValueError, AttributeError):
        return False
