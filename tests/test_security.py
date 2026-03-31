"""
Tests for app/security.py — password hashing / verification.

Run with:  pytest tests/test_security.py -v
"""

import pytest
from app.security import hash_password, verify_password


class TestHashPassword:
    def test_returns_string(self):
        h = hash_password("secret")
        assert isinstance(h, str)

    def test_format_salt_colon_hash(self):
        h = hash_password("secret")
        parts = h.split(":")
        assert len(parts) == 2, "Expected '<salt_hex>:<hash_hex>'"

    def test_salt_is_32_hex_chars(self):
        h = hash_password("secret")
        salt_hex = h.split(":")[0]
        assert len(salt_hex) == 32          # 16 bytes → 32 hex chars

    def test_unique_hashes_for_same_password(self):
        h1 = hash_password("password")
        h2 = hash_password("password")
        assert h1 != h2, "Two hashes of the same password must differ (random salt)"

    def test_empty_password(self):
        h = hash_password("")
        assert ":" in h


class TestVerifyPassword:
    def test_correct_password_returns_true(self):
        stored = hash_password("correct_horse_battery_staple")
        assert verify_password("correct_horse_battery_staple", stored) is True

    def test_wrong_password_returns_false(self):
        stored = hash_password("correct_horse_battery_staple")
        assert verify_password("wrong_password", stored) is False

    def test_empty_password_vs_non_empty_hash(self):
        stored = hash_password("nonempty")
        assert verify_password("", stored) is False

    def test_non_empty_password_vs_empty_hash(self):
        assert verify_password("something", "") is False

    def test_malformed_stored_hash_returns_false(self):
        assert verify_password("pw", "notahash") is False
        assert verify_password("pw", ":") is False
        assert verify_password("pw", "zz:zz") is False

    def test_unicode_password(self):
        pw = "pässwörd_日本語_🔑"
        stored = hash_password(pw)
        assert verify_password(pw, stored) is True
        assert verify_password("different", stored) is False

    def test_long_password(self):
        pw = "a" * 1000
        stored = hash_password(pw)
        assert verify_password(pw, stored) is True

    def test_roundtrip_multiple_passwords(self):
        passwords = ["", "a", "abc123", "P@$$w0rd!", "  spaces  "]
        for pw in passwords:
            stored = hash_password(pw)
            assert verify_password(pw, stored) is True, f"Failed for: {pw!r}"
