from app.db.base import get_cursor


def get_all():
    with get_cursor() as cr:
        cr.execute('SELECT * FROM survielance')
        return cr.fetchall()


def create(location: str, date: str, start_time: str,
           end_time: str, with_mask: str, without: str) -> None:
    with get_cursor(commit=True) as cr:
        cr.execute(
            'INSERT INTO survielance'
            ' (s_loc, dos, start_time, end_time, with_mask, without)'
            ' VALUES (%s,%s,%s,%s,%s,%s)',
            (location, date, start_time, end_time, with_mask, without),
        )
