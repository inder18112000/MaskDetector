from contextlib import contextmanager
import connection


@contextmanager
def get_cursor(commit: bool = False):
    """
    Open a DB connection, yield a cursor, then commit/rollback and close.

    Usage (read):
        with get_cursor() as cr:
            cr.execute('SELECT ...')
            return cr.fetchone()

    Usage (write):
        with get_cursor(commit=True) as cr:
            cr.execute('INSERT ...')
    """
    conn = connection.Connect()
    try:
        with conn.cursor() as cursor:
            yield cursor
            if commit:
                conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
