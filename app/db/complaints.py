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


def create(name: str, mobile: str, email: str, report: str, location: str) -> int:
    """Insert a new complaint and return the new complaint ID (cid)."""
    with get_cursor(commit=True) as cr:
        cr.execute(
            'INSERT INTO complaint (name, mobile, email, report, s_loc) VALUES (%s,%s,%s,%s,%s)',
            (name, mobile, email, report, location),
        )
        return cr.lastrowid


def update_status(location: str, status: str) -> None:
    """Bulk-update status for all complaints at a location (used after surveillance)."""
    with get_cursor(commit=True) as cr:
        cr.execute(
            'UPDATE complaint SET status=%s WHERE s_loc=%s',
            (status, location),
        )


def update_status_by_id(cid: int, status: str) -> None:
    """Update the status of a single complaint by its ID."""
    with get_cursor(commit=True) as cr:
        cr.execute(
            'UPDATE complaint SET status=%s WHERE cid=%s',
            (status, cid),
        )


def count_by_status(status: str) -> int:
    """Return the number of complaints with the given status."""
    with get_cursor() as cr:
        cr.execute('SELECT COUNT(*) FROM complaint WHERE status=%s', (status,))
        row = cr.fetchone()
        return row[0] if row else 0
