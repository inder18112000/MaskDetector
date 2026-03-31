"""
Backward-compatibility shim — redirects to the merged Dashboard class.
New code should import from app.views.dashboard directly.
"""
from app.views.dashboard import Dashboard, DARK_PALETTE  # noqa: F401


class dasboard:
    """Legacy entry point.  Accepts the old (result_tuple,) signature."""
    def __init__(self, result):
        from app.session import AppSession
        session = (result if isinstance(result, AppSession)
                   else AppSession.from_row(result, theme="dark"))
        Dashboard(session, DARK_PALETTE)
