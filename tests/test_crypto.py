"""Tests for envault.crypto encryption/decryption utilities."""

import pytest
from envault.crypto import encrypt, decrypt, derive_key, SALT_SIZE


PASSWORD = "super-secret-password"
PLAINTEXT = "DB_HOST=localhost\nDB_PASSWORD=hunter2\nAPI_KEY=abc123"


def test_encrypt_returns_bytes():
    result = encrypt(PLAINTEXT, PASSWORD)
    assert isinstance(result, bytes)


def test_encrypt_includes_salt_prefix():
    result = encrypt(PLAINTEXT, PASSWORD)
    # Must be longer than just the salt
    assert len(result) > SALT_SIZE


def test_encrypt_decrypt_roundtrip():
    ciphertext = encrypt(PLAINTEXT, PASSWORD)
    recovered = decrypt(ciphertext, PASSWORD)
    assert recovered == PLAINTEXT


def test_different_encryptions_produce_different_ciphertext():
    ct1 = encrypt(PLAINTEXT, PASSWORD)
    ct2 = encrypt(PLAINTEXT, PASSWORD)
    # Different salts should yield different outputs
    assert ct1 != ct2


def test_decrypt_wrong_password_raises_value_error():
    ciphertext = encrypt(PLAINTEXT, PASSWORD)
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt(ciphertext, "wrong-password")


def test_decrypt_malformed_ciphertext_raises_value_error():
    with pytest.raises(ValueError):
        decrypt(b"tooshort", PASSWORD)


def test_derive_key_is_deterministic():
    salt = b"\x00" * SALT_SIZE
    key1 = derive_key(PASSWORD, salt)
    key2 = derive_key(PASSWORD, salt)
    assert key1 == key2


def test_derive_key_differs_with_different_salts():
    key1 = derive_key(PASSWORD, b"\x00" * SALT_SIZE)
    key2 = derive_key(PASSWORD, b"\xff" * SALT_SIZE)
    assert key1 != key2


def test_encrypt_empty_string():
    ciphertext = encrypt("", PASSWORD)
    assert decrypt(ciphertext, PASSWORD) == ""
