from app.db.base import get_cursor


def get_all():
    with get_cursor() as cr:
        cr.execute('SELECT * FROM complaint')
        return cr.fetchall()


def get_by_location(location: str):
    with get_cursor() as cr:
        cr.execute('SELECT * FROM complaint WHERE s_loc LIKE %s', (location,))
        return cr.fetchall()


def get_by_email(email: str):
    """Return an existing complaint for this email, or None."""
    with get_cursor() as cr:
        cr.execute('SELECT * FROM complaint WHERE email=%s', (email,))
        return cr.fetchone()


def create(name: str, mobile: str, email: str, report: str, location: str) -> None:
    with get_cursor(commit=True) as cr:
        cr.execute(
            'INSERT INTO complaint (name, mobile, email, report, s_loc) VALUES (%s,%s,%s,%s,%s)',
            (name, mobile, email, report, location),
        )


def update_status(location: str, status: str) -> None:
    with get_cursor(commit=True) as cr:
        cr.execute(
            'UPDATE complaint SET status=%s WHERE s_loc=%s',
            (status, location),
        )
