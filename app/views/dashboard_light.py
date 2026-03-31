"""
Backward-compatibility shim — redirects to the merged Dashboard class.
New code should import from app.views.dashboard directly.
"""
from app.views.dashboard import Dashboard, LIGHT_PALETTE  # noqa: F401


class dasboard_light:
    """Legacy entry point.  Accepts the old (result_tuple,) signature."""
    def __init__(self, result):
        from app.session import AppSession
        session = (result if isinstance(result, AppSession)
                   else AppSession.from_row(result, theme="light"))
        Dashboard(session, LIGHT_PALETTE)
