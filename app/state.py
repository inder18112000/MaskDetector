"""
Backward-compatibility shim — kept so old import paths still work.

New code should use app.session.AppSession instead of these globals.
"""

from app.session import AppSession as _AppSession

# These three names are still importable for legacy callers.
result = None   # login row tuple OR AppSession instance
mode   = None   # 1 = dark, 2 = light  (use session.theme instead)
vid    = None   # cv2.VideoCapture      (use session.capture instead)
