from app.db.base import get_cursor


def get_all() -> list:
    """Return all surveillance location names as a flat list of strings."""
    with get_cursor() as cr:
        cr.execute('SELECT s_loc FROM surv_loc')
        return [row[0] for row in cr.fetchall()]


def exists(location: str) -> bool:
    with get_cursor() as cr:
        cr.execute('SELECT 1 FROM surv_loc WHERE s_loc = %s', (location,))
        return cr.fetchone() is not None


def create(location: str) -> None:
    with get_cursor(commit=True) as cr:
        cr.execute('INSERT INTO surv_loc (s_loc) VALUES (%s)', (location,))
