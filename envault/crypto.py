"""Encryption and decryption utilities for envault vaults."""

import os
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet, InvalidToken


SALT_SIZE = 16
ITERATIONS = 390_000


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a Fernet-compatible key from a password and salt using PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
    )
    raw_key = kdf.derive(password.encode("utf-8"))
    return base64.urlsafe_b64encode(raw_key)


def encrypt(plaintext: str, password: str) -> bytes:
    """
    Encrypt plaintext using a password.

    Returns salt + encrypted token as raw bytes.
    """
    salt = os.urandom(SALT_SIZE)
    key = derive_key(password, salt)
    fernet = Fernet(key)
    token = fernet.encrypt(plaintext.encode("utf-8"))
    return salt + token


def decrypt(ciphertext: bytes, password: str) -> str:
    """
    Decrypt ciphertext using a password.

    Expects ciphertext in the format: salt + encrypted token.
    Raises ValueError on bad password or corrupted data.
    """
    if len(ciphertext) <= SALT_SIZE:
        raise ValueError("Ciphertext is too short or malformed.")

    salt = ciphertext[:SALT_SIZE]
    token = ciphertext[SALT_SIZE:]
    key = derive_key(password, salt)
    fernet = Fernet(key)

    try:
        plaintext = fernet.decrypt(token)
    except InvalidToken as exc:
        raise ValueError(
            "Decryption failed: invalid password or corrupted vault."
        ) from exc

    return plaintext.decode("utf-8")
