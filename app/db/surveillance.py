from app.db.base import get_cursor


def get_all():
    """Return all surveillance sessions with city, place, and area from surv_loc.

    Returns 10-tuples:
    (sid, city, place_name, area, dos, start_time, end_time,
     with_mask, without, total_persons)
    For legacy rows where area is empty, area falls back to s_loc.
    """
    with get_cursor() as cr:
        cr.execute(
            'SELECT s.sid,'
            '       COALESCE(l.city, \'\') AS city,'
            '       COALESCE(l.place_name, \'\') AS place_name,'
            '       COALESCE(NULLIF(l.area, \'\'), s.s_loc) AS area,'
            '       s.dos, s.start_time, s.end_time,'
            '       s.with_mask, s.without, s.total_persons'
            ' FROM survielance s'
            ' LEFT JOIN surv_loc l ON s.s_loc = l.s_loc'
            ' ORDER BY s.sid DESC'
        )
        return cr.fetchall()


def count_today() -> int:
    """Return the number of surveillance sessions recorded today."""
    with get_cursor() as cr:
        cr.execute(
            'SELECT COUNT(*) FROM survielance WHERE dos = CURDATE()'
        )
        row = cr.fetchone()
        return row[0] if row else 0


def get_filtered(from_date: str, to_date: str, location: str):
    """Return sessions filtered by date range and optionally location.

    Parameters match the format used by get_all().
    Pass location='' to skip the location filter.
    """
    with get_cursor() as cr:
        if location:
            cr.execute(
                'SELECT s.sid,'
                '       COALESCE(l.city, \'\') AS city,'
                '       COALESCE(l.place_name, \'\') AS place_name,'
                '       COALESCE(NULLIF(l.area, \'\'), s.s_loc) AS area,'
                '       s.dos, s.start_time, s.end_time,'
                '       s.with_mask, s.without, s.total_persons'
                ' FROM survielance s'
                ' LEFT JOIN surv_loc l ON s.s_loc = l.s_loc'
                ' WHERE s.dos BETWEEN %s AND %s AND s.s_loc = %s'
                ' ORDER BY s.sid DESC',
                (from_date, to_date, location),
            )
        else:
            cr.execute(
                'SELECT s.sid,'
                '       COALESCE(l.city, \'\') AS city,'
                '       COALESCE(l.place_name, \'\') AS place_name,'
                '       COALESCE(NULLIF(l.area, \'\'), s.s_loc) AS area,'
                '       s.dos, s.start_time, s.end_time,'
                '       s.with_mask, s.without, s.total_persons'
                ' FROM survielance s'
                ' LEFT JOIN surv_loc l ON s.s_loc = l.s_loc'
                ' WHERE s.dos BETWEEN %s AND %s'
                ' ORDER BY s.sid DESC',
                (from_date, to_date),
            )
        return cr.fetchall()


def create(location: str, date: str, start_time: str,
           end_time: str, with_mask: str, without: str,
           total_persons: int = 0) -> None:
    with get_cursor(commit=True) as cr:
        cr.execute(
            'INSERT INTO survielance'
            ' (s_loc, dos, start_time, end_time, with_mask, without, total_persons)'
            ' VALUES (%s,%s,%s,%s,%s,%s,%s)',
            (location, date, start_time, end_time, with_mask, without, total_persons),
        )
