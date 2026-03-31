"""
Tests for app/session.py — AppSession dataclass.

Run with:  pytest tests/test_session.py -v
"""

import pytest
from app.session import AppSession


_ROW = ("admin_user", "admin@example.com", "salt:hash", "Admin")
_SUPER_ROW = ("super", "super@example.com", "salt:hash", "Super Admin")


class TestAppSessionFromRow:
    def test_fields_populated(self):
        s = AppSession.from_row(_ROW)
        assert s.username      == "admin_user"
        assert s.email         == "admin@example.com"
        assert s.password_hash == "salt:hash"
        assert s.role          == "Admin"

    def test_default_theme_is_light(self):
        s = AppSession.from_row(_ROW)
        assert s.theme == "light"

    def test_explicit_dark_theme(self):
        s = AppSession.from_row(_ROW, theme="dark")
        assert s.theme == "dark"

    def test_is_super_admin_false_for_admin(self):
        s = AppSession.from_row(_ROW)
        assert s.is_super_admin is False

    def test_is_super_admin_true_for_super(self):
        s = AppSession.from_row(_SUPER_ROW)
        assert s.is_super_admin is True


class TestAsTuple:
    def test_returns_four_tuple(self):
        s = AppSession.from_row(_ROW)
        t = s.as_tuple()
        assert t == _ROW


class TestCaptureLifecycle:
    def test_capture_initially_none(self):
        s = AppSession.from_row(_ROW)
        assert s.capture is None

    def test_capture_can_be_set(self):
        s = AppSession.from_row(_ROW)
        fake_cap = object()
        s.capture = fake_cap
        assert s.capture is fake_cap

    def test_release_capture_calls_release(self):
        from unittest.mock import MagicMock
        s = AppSession.from_row(_ROW)
        mock_cap = MagicMock()
        s.capture = mock_cap
        s.release_capture()
        mock_cap.release.assert_called_once()
        assert s.capture is None

    def test_release_capture_when_none_is_safe(self):
        s = AppSession.from_row(_ROW)
        s.release_capture()   # should not raise

    def test_release_capture_handles_exception(self):
        from unittest.mock import MagicMock
        s = AppSession.from_row(_ROW)
        bad_cap = MagicMock()
        bad_cap.release.side_effect = RuntimeError("camera gone")
        s.capture = bad_cap
        s.release_capture()   # should swallow the exception
        assert s.capture is None
