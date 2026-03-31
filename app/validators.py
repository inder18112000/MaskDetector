"""
Shared form-validation helpers.

All functions show a tkinter error dialog on failure and return False.
On success they return True without showing any dialog.

Usage:
    from app.validators import require, valid_email, valid_phone

    if not require([("Full Name", self.name_e), ("Email", self.email_e)]):
        return
    if not valid_email(self.email_e.get(), self.email_e):
        return
"""

import re
from tkinter.messagebox import showerror

_EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
_PHONE_RE = re.compile(r'^\+?[\d\s\-(). ]{7,20}$')


def _focus(widget) -> None:
    try:
        widget.focus()
    except Exception:
        pass


def require(fields: list) -> bool:
    """
    Check that every (label, widget) pair has a non-empty value.

    Parameters
    ----------
    fields : list of (label_str, widget)
        widget must support .get() — Entry, Combobox, StringVar, etc.

    Returns False (and shows error dialog) on the first empty field.
    Returns True when all fields are filled.
    """
    for label, widget in fields:
        try:
            val = widget.get().strip()
        except AttributeError:
            val = str(widget).strip()
        if not val:
            showerror("Missing Field", f"Please enter {label}.")
            _focus(widget)
            return False
    return True


def valid_email(email: str, widget=None) -> bool:
    """Return True if email matches a basic RFC-compatible pattern."""
    if not _EMAIL_RE.match(email):
        showerror("Invalid Email", "Please enter a valid email address.")
        _focus(widget)
        return False
    return True


def valid_phone(phone: str, widget=None) -> bool:
    """Return True if phone is 7–20 digits (with optional spaces/dashes)."""
    if not _PHONE_RE.match(phone):
        showerror("Invalid Phone",
                  "Please enter a valid phone number (7–20 digits).")
        _focus(widget)
        return False
    return True
