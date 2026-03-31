"""
Typed application session — replaces the three bare globals in state.py.

Usage:
    from app.session import AppSession

    # Build from a DB login row (username, email, password_hash, role)
    session = AppSession.from_row(row, theme="light")

    # Access fields
    session.username
    session.role
    session.is_super_admin   # bool property

    # Camera lifetime management
    session.capture = my_video_capture_obj
    session.release_capture()     # safe even if capture is None
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional


@dataclass
class AppSession:
    username:      str
    email:         str
    password_hash: str
    role:          str
    theme: Literal["dark", "light"] = "light"
    _capture: Optional[object]      = field(default=None, repr=False)

    # ── factory ───────────────────────────────────────────────────────────────
    @classmethod
    def from_row(cls, row: tuple,
                 theme: Literal["dark", "light"] = "light") -> "AppSession":
        """Create a session from a DB login row (username, email, pw_hash, role)."""
        return cls(
            username=row[0],
            email=row[1],
            password_hash=row[2],
            role=row[3],
            theme=theme,
        )

    # ── derived properties ────────────────────────────────────────────────────
    @property
    def is_super_admin(self) -> bool:
        return self.role == "Super Admin"

    def as_tuple(self) -> tuple:
        """Return (username, email, password_hash, role) — backward-compat."""
        return (self.username, self.email, self.password_hash, self.role)

    # ── camera capture lifecycle ──────────────────────────────────────────────
    @property
    def capture(self):
        return self._capture

    @capture.setter
    def capture(self, val) -> None:
        self._capture = val

    def release_capture(self) -> None:
        """Release the video capture if one is held, then clear the reference."""
        if self._capture is not None:
            try:
                self._capture.release()
            except Exception:
                pass
            self._capture = None
