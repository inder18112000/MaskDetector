# MaskDetector — Claude Code Instructions

## Project Overview
Desktop Tkinter + OpenCV surveillance app. YOLOv8 detects mask compliance via webcam. MySQL on AWS stores sessions, complaints, and admin accounts. GUI is entirely custom-drawn (Canvas-based `StyledButton` for macOS compatibility).

## Running the App
```bash
python3 main.py
```

## Running Tests
```bash
python3 -m pytest tests/ -v
```
All 48 tests must pass. Tests cover: `app/security.py`, `app/validators.py`, `app/session.py`, `app/camera/tracker.py`.

## Architecture

### Entry Points
- `main.py` → opens `app/views/login.py` (`log` class)
- `setup_admin.py` → interactive CLI to create the first Super Admin

### Key Modules
| File | Purpose |
|---|---|
| `app/views/dashboard.py` | Merged dashboard (dark + light). Single `Dashboard` class parameterised by `ThemePalette`. |
| `app/views/login.py` | Login screen + 2FA OTP flow |
| `app/views/forgot_password.py` | Reset password — opens as `Toplevel(parent)` modal over login |
| `app/views/complaint.py` | Public complaint form |
| `app/db/base.py` | Versioned migration system (`schema_version` table). Add new migrations here. |
| `app/db/complaints.py` | CRUD for `complaint` table |
| `app/db/surveillance.py` | CRUD for `survielance` table (note intentional spelling) |
| `app/session.py` | `AppSession` dataclass — typed replacement for `state.py` globals |
| `app/security.py` | `hash_password` / `verify_password` (PBKDF2-HMAC-SHA256) |
| `app/validators.py` | `require()`, `valid_email()`, `valid_phone()` |
| `app/theme.py` | All colors, fonts, `StyledButton`, `btn()`, `style_treeview()` |
| `app/logger.py` | Named loggers. File handler (DEBUG → `maskdetector.log`), stderr (WARNING+). |
| `otp.py` | Gmail SMTP OTP sender with rate limiting (3 attempts / 5 min) |
| `connection.py` | PyMySQL connection from `.env` |

### Theme System
`ThemePalette` dataclass in `dashboard.py` holds all colors. Two constants: `DARK_PALETTE`, `LIGHT_PALETTE`. Key color roles:
- `panel` / `panel_fg` / `panel_muted` — sidebar and nav bar colors
- `bg` / `card` / `fg` / `muted` — main area and content
- `inp` / `border` — entry fields and dividers

**Rule**: text ON panel backgrounds must use `panel_fg` (primary) or `panel_muted` (secondary), NOT `muted` (which is for card/content areas).

### Database Migrations
Add new migrations to `_MIGRATIONS` in `app/db/base.py`:
```python
def _m7_my_change(conn) -> None:
    with conn.cursor() as c:
        c.execute("...")   # must be idempotent (use IF NOT EXISTS / INSERT IGNORE)
    conn.commit()

_MIGRATIONS = [
    ...
    {"id": 7, "desc": "My change", "up": _m7_my_change},
]
```
Migrations auto-run once on first DB access per process. Never reuse or reorder IDs.

### Navigation Patterns
- **Full window screens**: `Login`, `Complaint`, `Dashboard` — each creates its own `Tk()` root.
- **Modals**: `Forgot Password`, Add Location dialog, Admin Edit/Create, Complaint Status — all `Toplevel(parent)` with `grab_set()`.
- **Inline panels**: Complaints list, History, Admin Management — replace `main_frame` content via `_clear_main()` / `_restore_placeholder()`.

### Role System
- `Super Admin` — full access (add admin, manage locations, all panels)
- `Admin` — view complaints, history, run surveillance; cannot manage admins or locations

## Environment Variables (`.env`)
```
DB_HOST=
DB_USER=
DB_PASSWORD=
DB_NAME=
EMAIL_SENDER=
EMAIL_PASSWORD=
```

## Coding Conventions
- Custom buttons: always use `theme.btn(parent, text, command, ...)` — never `tk.Button` (breaks on macOS)
- DB access: always through `app.db.base.get_cursor()` context manager
- Logging: `from app.logger import get; _log = get(__name__)`
- Passwords: always `hash_password()` on write, `verify_password()` on check — never store plain text
- SQL: always use `%s` placeholders — never f-strings in queries

## Database Tables
`login` · `cities` · `surv_loc` · `complaint` · `survielance` · `schema_version`

Note: `survielance` is an intentional spelling from the original schema — do not rename.
