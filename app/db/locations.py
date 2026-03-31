from app.db.base import get_cursor


def get_all() -> list:
    """Return all surveillance location area names as a flat list of strings."""
    with get_cursor() as cr:
        cr.execute('SELECT s_loc FROM surv_loc ORDER BY s_loc')
        return [row[0] for row in cr.fetchall()]


def get_all_with_city() -> list:
    """Return list of (s_loc, city, place_name, area) tuples for display."""
    with get_cursor() as cr:
        cr.execute(
            'SELECT s_loc, city, place_name, area '
            'FROM surv_loc ORDER BY city, place_name, s_loc'
        )
        return cr.fetchall()


def get_city(location: str) -> str:
    """Return the city for a given area name, or empty string if not found."""
    with get_cursor() as cr:
        cr.execute('SELECT city FROM surv_loc WHERE s_loc = %s', (location,))
        row = cr.fetchone()
        return row[0] if row else ''


def exists(location: str) -> bool:
    with get_cursor() as cr:
        cr.execute('SELECT 1 FROM surv_loc WHERE s_loc = %s', (location,))
        return cr.fetchone() is not None


def create(location: str, city: str,
           place_name: str = '', area: str = '') -> None:
    with get_cursor(commit=True) as cr:
        cr.execute(
            'INSERT INTO surv_loc (s_loc, city, place_name, area) '
            'VALUES (%s, %s, %s, %s)',
            (location, city, place_name, area),
        )
