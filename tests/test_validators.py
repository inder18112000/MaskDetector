"""
Tests for app/validators.py — form validation helpers.

These tests mock tkinter.messagebox so no display is needed.

Run with:  pytest tests/test_validators.py -v
"""

import pytest
from unittest.mock import patch, MagicMock


# ── helpers ───────────────────────────────────────────────────────────────────

def _entry(value: str):
    """Return a mock widget whose .get() returns *value*."""
    m = MagicMock()
    m.get.return_value = value
    return m


# ── require() ─────────────────────────────────────────────────────────────────

class TestRequire:
    @patch("app.validators.showerror")
    def test_all_filled_returns_true(self, mock_err):
        from app.validators import require
        assert require([("Name", _entry("Alice")),
                        ("Email", _entry("a@b.com"))]) is True
        mock_err.assert_not_called()

    @patch("app.validators.showerror")
    def test_empty_field_returns_false(self, mock_err):
        from app.validators import require
        result = require([("Name", _entry(""))])
        assert result is False
        mock_err.assert_called_once()

    @patch("app.validators.showerror")
    def test_whitespace_only_counts_as_empty(self, mock_err):
        from app.validators import require
        result = require([("Name", _entry("   "))])
        assert result is False
        mock_err.assert_called_once()

    @patch("app.validators.showerror")
    def test_stops_at_first_empty_field(self, mock_err):
        from app.validators import require
        result = require([
            ("Name",  _entry("")),
            ("Email", _entry("a@b.com")),
        ])
        assert result is False
        assert mock_err.call_count == 1   # only one error shown


# ── valid_email() ─────────────────────────────────────────────────────────────

class TestValidEmail:
    @patch("app.validators.showerror")
    def test_valid_email_returns_true(self, mock_err):
        from app.validators import valid_email
        assert valid_email("user@example.com") is True
        mock_err.assert_not_called()

    @patch("app.validators.showerror")
    def test_missing_at_sign_returns_false(self, mock_err):
        from app.validators import valid_email
        assert valid_email("notanemail") is False
        mock_err.assert_called_once()

    @patch("app.validators.showerror")
    def test_missing_domain_returns_false(self, mock_err):
        from app.validators import valid_email
        assert valid_email("user@") is False

    @patch("app.validators.showerror")
    def test_empty_string_returns_false(self, mock_err):
        from app.validators import valid_email
        assert valid_email("") is False


# ── valid_phone() ─────────────────────────────────────────────────────────────

class TestValidPhone:
    @patch("app.validators.showerror")
    def test_plain_digits_valid(self, mock_err):
        from app.validators import valid_phone
        assert valid_phone("9876543210") is True
        mock_err.assert_not_called()

    @patch("app.validators.showerror")
    def test_international_format_valid(self, mock_err):
        from app.validators import valid_phone
        assert valid_phone("+91 98765 43210") is True

    @patch("app.validators.showerror")
    def test_too_short_returns_false(self, mock_err):
        from app.validators import valid_phone
        assert valid_phone("123") is False
        mock_err.assert_called_once()

    @patch("app.validators.showerror")
    def test_letters_returns_false(self, mock_err):
        from app.validators import valid_phone
        assert valid_phone("ABCDEFGHIJ") is False
