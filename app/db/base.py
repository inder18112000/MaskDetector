from contextlib import contextmanager
import connection
from app.logger import get

_log = get(__name__)

# ── Versioned migration system ────────────────────────────────────────────────
#
# Each migration is a dict:
#   id       — unique integer, monotonically increasing (never reuse or reorder)
#   desc     — human-readable description shown in the log
#   up()     — callable(conn) that performs the migration; must be idempotent
#
# The `schema_version` table stores the highest applied migration id.
# On first run, all migrations with id > current_version are applied in order.
# ─────────────────────────────────────────────────────────────────────────────

_migrated = False  # in-process guard — migrations run once per process

_SEED_CITIES = [
    'Ahmedabad', 'Amritsar',  'Bengaluru', 'Chandigarh', 'Chennai',
    'Delhi',     'Hyderabad', 'Jaipur',    'Kolkata',    'Lucknow',
    'Mumbai',    'Noida',     'Patna',     'Pune',       'Surat',
]


def _col_exists(c, table: str, column: str) -> bool:
    c.execute(
        "SELECT COUNT(*) FROM information_schema.COLUMNS "
        "WHERE TABLE_SCHEMA = DATABASE() "
        "AND TABLE_NAME = %s AND COLUMN_NAME = %s",
        (table, column),
    )
    return c.fetchone()[0] > 0


def _add_col(c, table: str, column: str, definition: str) -> None:
    if not _col_exists(c, table, column):
        c.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
        _log.info("Added column %s.%s", table, column)


# ── migration definitions ─────────────────────────────────────────────────────

def _m1_create_cities(conn) -> None:
    with conn.cursor() as c:
        c.execute(
            "CREATE TABLE IF NOT EXISTS cities "
            "(city_name VARCHAR(100) NOT NULL, PRIMARY KEY (city_name))"
        )
    conn.commit()


def _m2_surv_loc_city(conn) -> None:
    with conn.cursor() as c:
        _add_col(c, "surv_loc", "city", "VARCHAR(100) NOT NULL DEFAULT ''")
    conn.commit()


def _m3_survielance_total_persons(conn) -> None:
    with conn.cursor() as c:
        _add_col(c, "survielance", "total_persons", "INT NOT NULL DEFAULT 0")
    conn.commit()


def _m4_surv_loc_place_area(conn) -> None:
    with conn.cursor() as c:
        _add_col(c, "surv_loc", "place_name", "VARCHAR(200) NOT NULL DEFAULT ''")
        _add_col(c, "surv_loc", "area",       "VARCHAR(100) NOT NULL DEFAULT ''")
    conn.commit()


def _m5_seed_cities(conn) -> None:
    with conn.cursor() as c:
        # Backfill from existing surv_loc rows
        c.execute(
            "INSERT IGNORE INTO cities (city_name) "
            "SELECT DISTINCT city FROM surv_loc WHERE city != ''"
        )
        # Seed pre-defined list if still empty
        c.execute("SELECT COUNT(*) FROM cities")
        if c.fetchone()[0] == 0:
            c.executemany(
                "INSERT IGNORE INTO cities (city_name) VALUES (%s)",
                [(name,) for name in _SEED_CITIES],
            )
            _log.info("Seeded %d cities", len(_SEED_CITIES))
    conn.commit()


_SEED_LOCATIONS = [
    # (s_loc PK,                           city,        place_name,                    area)
    ("AIIMS — Main Gate",               "Delhi",     "AIIMS",               "Main Gate"),
    ("Connaught Place — Metro Exit",    "Delhi",     "Connaught Place",     "Metro Exit"),
    ("India Gate — North Gate",         "Delhi",     "India Gate",          "North Gate"),
    ("CST Station — Entry Hall",        "Mumbai",    "CST Station",         "Entry Hall"),
    ("Marine Drive — Promenade",        "Mumbai",    "Marine Drive",        "Promenade"),
    ("BKC — Office Complex",            "Mumbai",    "BKC",                 "Office Complex"),
    ("Cubbon Park — East Gate",         "Bengaluru", "Cubbon Park",         "East Gate"),
    ("Koramangala — Food Street",       "Bengaluru", "Koramangala",         "Food Street"),
    ("Marina Beach — North End",        "Chennai",   "Marina Beach",        "North End"),
    ("T. Nagar — Shopping Complex",     "Chennai",   "T. Nagar",            "Shopping Complex"),
    ("Sector 17 — Plaza",               "Chandigarh","Sector 17",           "Plaza"),
    ("PGI — OPD Block",                 "Chandigarh","PGI",                 "OPD Block"),
]

_SEED_COMPLAINTS = [
    # (name, mobile, email, report, s_loc, status)
    ("Aditya Nair",   "9811122334", "aditya.nair@example.com",
     "Visitors entering AIIMS without masks at the main gate.",
     "AIIMS — Main Gate",            "Pending"),
    ("Sunita Verma",  "9922334455", "sunita.verma@example.com",
     "Metro commuters ignoring mask rules at Connaught Place exit.",
     "Connaught Place — Metro Exit", "Under Review"),
    ("Karan Singh",   "9033445566", "karan.singh@example.com",
     "Tourist crowd near India Gate not wearing masks.",
     "India Gate — North Gate",      "Pending"),
    ("Meera Pillai",  "9144556677", "meera.pillai@example.com",
     "Train passengers at CST not following mask mandate.",
     "CST Station — Entry Hall",     "Surveillance Done"),
    ("Rohit Desai",   "9255667788", "rohit.desai@example.com",
     "Evening walkers on Marine Drive not wearing masks.",
     "Marine Drive — Promenade",     "Pending"),
    ("Pooja Iyer",    "9366778899", "pooja.iyer@example.com",
     "Office employees at BKC tech park not complying with mask policy.",
     "BKC — Office Complex",         "Under Review"),
    ("Vikram Reddy",  "9477889900", "vikram.reddy@example.com",
     "Park visitors at Cubbon Park ignoring mask guidelines.",
     "Cubbon Park — East Gate",      "Dismissed"),
    ("Anjali Bose",   "9588990011", "anjali.bose@example.com",
     "Food stall visitors at Koramangala without masks.",
     "Koramangala — Food Street",    "Pending"),
    ("Suresh Menon",  "9699001122", "suresh.menon@example.com",
     "Beach-goers at Marina Beach North End not wearing masks.",
     "Marina Beach — North End",     "Surveillance Done"),
    ("Deepa Joshi",   "9700112233", "deepa.joshi@example.com",
     "Shoppers at T. Nagar market area not wearing masks.",
     "T. Nagar — Shopping Complex",  "Pending"),
    ("Naveen Gupta",  "9811223344", "naveen.gupta@example.com",
     "Crowded Sector 17 plaza with very low mask compliance.",
     "Sector 17 — Plaza",            "Pending"),
    ("Ananya Das",    "9922334456", "ananya.das@example.com",
     "OPD visitors at PGI not following mask protocol.",
     "PGI — OPD Block",              "Under Review"),
]

_SEED_SESSIONS = [
    # (s_loc, dos, start_time, end_time, with_mask, without, total_persons)
    ("AIIMS — Main Gate",            "2025-11-10", "08:00:00", "08:45:00", "91.0 %",  "9.0 %",  44),
    ("Connaught Place — Metro Exit", "2025-11-12", "10:30:00", "11:15:00", "78.5 %",  "21.5 %", 65),
    ("India Gate — North Gate",      "2025-11-14", "16:00:00", "16:30:00", "55.0 %",  "45.0 %", 20),
    ("CST Station — Entry Hall",     "2025-11-15", "07:30:00", "08:30:00", "83.0 %",  "17.0 %", 118),
    ("Marine Drive — Promenade",     "2025-11-18", "18:00:00", "18:45:00", "66.0 %",  "34.0 %", 50),
    ("BKC — Office Complex",         "2025-11-20", "09:00:00", "09:30:00", "97.0 %",  "3.0 %",  72),
    ("Cubbon Park — East Gate",      "2025-12-02", "07:00:00", "07:40:00", "89.0 %",  "11.0 %", 36),
    ("Marina Beach — North End",     "2025-12-05", "17:00:00", "17:45:00", "62.0 %",  "38.0 %", 85),
    ("Sector 17 — Plaza",            "2025-12-10", "11:00:00", "11:30:00", "75.0 %",  "25.0 %", 28),
    ("PGI — OPD Block",              "2025-12-15", "08:30:00", "09:15:00", "94.0 %",  "6.0 %",  51),
    ("Main Gate",                    "2024-03-05", "09:00:00", "09:30:00", "82.0 %",  "18.0 %", 33),
    ("Canteen",                      "2024-03-06", "12:00:00", "12:30:00", "70.0 %",  "30.0 %", 40),
    ("Library",                      "2024-03-07", "10:00:00", "10:20:00", "95.0 %",  "5.0 %",  22),
]


def _m6_seed_demo_data(conn) -> None:
    with conn.cursor() as c:
        c.executemany(
            "INSERT IGNORE INTO surv_loc (s_loc, city, place_name, area) "
            "VALUES (%s, %s, %s, %s)",
            _SEED_LOCATIONS,
        )
        c.executemany(
            "INSERT IGNORE INTO complaint (name, mobile, email, report, s_loc, status) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            _SEED_COMPLAINTS,
        )
        c.executemany(
            "INSERT IGNORE INTO survielance "
            "(s_loc, dos, start_time, end_time, with_mask, without, total_persons) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            _SEED_SESSIONS,
        )
        _log.info(
            "Seeded %d locations, %d complaints, %d sessions",
            len(_SEED_LOCATIONS), len(_SEED_COMPLAINTS), len(_SEED_SESSIONS),
        )
    conn.commit()


_MIGRATIONS = [
    {"id": 1, "desc": "Create cities table",                "up": _m1_create_cities},
    {"id": 2, "desc": "Add surv_loc.city column",           "up": _m2_surv_loc_city},
    {"id": 3, "desc": "Add survielance.total_persons",      "up": _m3_survielance_total_persons},
    {"id": 4, "desc": "Add surv_loc.place_name / area",     "up": _m4_surv_loc_place_area},
    {"id": 5, "desc": "Seed cities table",                  "up": _m5_seed_cities},
    {"id": 6, "desc": "Seed demo locations, complaints, sessions",
                                                            "up": _m6_seed_demo_data},
]


def _ensure_version_table(conn) -> None:
    with conn.cursor() as c:
        c.execute(
            "CREATE TABLE IF NOT EXISTS schema_version "
            "(version INT NOT NULL DEFAULT 0, PRIMARY KEY (version))"
        )
        c.execute("SELECT COUNT(*) FROM schema_version")
        if c.fetchone()[0] == 0:
            c.execute("INSERT INTO schema_version (version) VALUES (0)")
    conn.commit()


def _get_version(conn) -> int:
    with conn.cursor() as c:
        c.execute("SELECT version FROM schema_version LIMIT 1")
        row = c.fetchone()
        return row[0] if row else 0


def _set_version(conn, version: int) -> None:
    with conn.cursor() as c:
        c.execute("UPDATE schema_version SET version = %s", (version,))
    conn.commit()


def _run_migrations(conn) -> None:
    global _migrated
    if _migrated:
        return
    _migrated = True

    try:
        _ensure_version_table(conn)
        current = _get_version(conn)
        _log.debug("Schema version: %d", current)

        pending = [m for m in _MIGRATIONS if m["id"] > current]
        if not pending:
            return

        for m in pending:
            try:
                m["up"](conn)
                _set_version(conn, m["id"])
                _log.info("Migration %d applied: %s", m["id"], m["desc"])
            except Exception:
                _log.exception("Migration %d failed: %s", m["id"], m["desc"])
                try:
                    conn.rollback()
                except Exception:
                    pass
    except Exception:
        _log.exception("Migration system error")
# ─────────────────────────────────────────────────────────────────────────────


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
    _run_migrations(conn)
    try:
        with conn.cursor() as cursor:
            yield cursor
            if commit:
                conn.commit()
    except Exception:
        _log.exception("DB operation failed — rolling back")
        conn.rollback()
        raise
    finally:
        conn.close()
