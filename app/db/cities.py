from app.db.base import get_cursor


def get_all() -> list:
    """Return all city names as a sorted flat list."""
    with get_cursor() as cr:
        cr.execute('SELECT city_name FROM cities ORDER BY city_name')
        return [row[0] for row in cr.fetchall()]


def exists(city_name: str) -> bool:
    with get_cursor() as cr:
        cr.execute('SELECT 1 FROM cities WHERE city_name = %s', (city_name,))
        return cr.fetchone() is not None


def create(city_name: str) -> None:
    with get_cursor(commit=True) as cr:
        cr.execute(
            'INSERT INTO cities (city_name) VALUES (%s)',
            (city_name,),
        )
