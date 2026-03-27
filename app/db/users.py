from app.db.base import get_cursor


def get_by_email(email: str):
    """Return the login row for the given email, or None."""
    with get_cursor() as cr:
        cr.execute('SELECT * FROM login WHERE email=%s', (email,))
        return cr.fetchone()


def get_all():
    """Return (username, email, role) for every admin account."""
    with get_cursor() as cr:
        cr.execute('SELECT username, email, role FROM login')
        return cr.fetchall()


def create(username: str, email: str, password_hash: str, role: str) -> None:
    with get_cursor(commit=True) as cr:
        cr.execute(
            'INSERT INTO login (username, email, password, role) VALUES (%s,%s,%s,%s)',
            (username, email, password_hash, role),
        )


def update(email: str, username: str, role: str) -> None:
    with get_cursor(commit=True) as cr:
        cr.execute(
            'UPDATE login SET username=%s, role=%s WHERE email=%s',
            (username, role, email),
        )


def update_password(email: str, password_hash: str) -> None:
    with get_cursor(commit=True) as cr:
        cr.execute(
            'UPDATE login SET password=%s WHERE email=%s',
            (password_hash, email),
        )


def delete(email: str) -> None:
    with get_cursor(commit=True) as cr:
        cr.execute('DELETE FROM login WHERE email=%s', (email,))
