# MaskDetector

A desktop surveillance application that uses computer vision to detect mask compliance across monitored locations. It helps governments decide whether to implement lockdowns or restrictions based on real-time mask-wearing data collected from surveillance zones.

---

## Features

- Real-time face and mask detection via webcam using OpenCV Haar Cascades
- Dark mode and light mode dashboards
- Role-based access: **Super Admin** (OTP-verified) and **Admin**
- Surveillance session recording with masked/unmasked population statistics
- Pie chart visualisation of mask compliance after each session
- Complaint registration for users to report violations
- Admin management: add, update, delete admins
- Surveillance history viewer
- OTP-based login verification and password reset via email

---

## Project Structure

```
MaskDetector/
├── main.py                        # Entry point
├── connection.py                  # Database connection (reads from .env)
├── otp.py                         # OTP email sender (reads from .env)
├── sms_sending.py                 # SMS stub (configure a provider to enable)
├── requirements.txt
├── .env                           # Credentials — do NOT commit
├── .env.example                   # Template for .env
│
├── assets/
│   ├── images/                    # UI background and icon images
│   │   ├── icon.png
│   │   ├── front_login.png
│   │   ├── comp_bg.png
│   │   ├── add.png
│   │   ├── bg_fg.png
│   │   └── dashboard.png
│   └── cascades/                  # OpenCV Haar Cascade classifiers
│       ├── front1.xml
│       ├── haarcascade_mcs_mouth.xml
│       ├── haarcascade_frontalface_default.xml
│       └── haarcascade_upperbody.xml
│
└── app/
    ├── state.py                   # Shared global state (result, mode, vid)
    ├── paths.py                   # Centralised asset path constants
    ├── camera/
    │   └── video_capture.py       # Video capture wrapper (MyVideoCapture)
    └── views/
        ├── login.py               # Login screen + OTP verification
        ├── complaint.py           # User complaint registration form
        ├── complaint_show.py      # Admin view of registered complaints
        ├── surveillance_history.py# Surveillance session history table
        ├── admin_view.py          # View / edit / delete admins
        ├── admin_add.py           # Add new admin user
        ├── forgot_password.py     # OTP-based password reset
        ├── dashboard_dark.py      # Super Admin dashboard (dark theme)
        └── dashboard_light.py     # Admin dashboard (light theme)
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| GUI | Python Tkinter |
| Computer Vision | OpenCV (Haar Cascade classifiers) |
| Image Processing | Pillow (PIL) |
| Database | MySQL (hosted on AWS) |
| DB Connector | PyMySQL |
| Data Visualisation | Matplotlib |
| Email / OTP | smtplib + Gmail SMTP |
| Config | python-dotenv |

---

## Prerequisites

- Python 3.8+
- A running MySQL database
- A Gmail account with an [App Password](https://myaccount.google.com/apppasswords) enabled (required for OTP email)
- A webcam (for live surveillance)

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/inder18112000/MaskDetector.git
cd MaskDetector
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate       # macOS / Linux
venv\Scripts\activate          # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```env
DB_HOST=your_database_host
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_NAME=your_database_name

EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
```

> **Note:** Use a Gmail [App Password](https://myaccount.google.com/apppasswords), not your regular Gmail password.

### 5. Set up the database

Run the setup script to create all tables:

```bash
mysql -u <user> -p <database_name> < database_setup.sql
```

This creates the following tables:

```sql
CREATE TABLE IF NOT EXISTS login (
    username VARCHAR(100)        NOT NULL,
    email    VARCHAR(100)        NOT NULL,
    password VARCHAR(200)        NOT NULL,
    role     VARCHAR(50)         NOT NULL,
    PRIMARY KEY (email)
);

CREATE TABLE IF NOT EXISTS surv_loc (
    s_loc VARCHAR(100) NOT NULL,
    PRIMARY KEY (s_loc)
);

CREATE TABLE IF NOT EXISTS complaint (
    cid    INT          NOT NULL AUTO_INCREMENT,
    name   VARCHAR(100) NOT NULL,
    mobile VARCHAR(20)  NOT NULL,
    email  VARCHAR(100) NOT NULL,
    report TEXT         NOT NULL,
    s_loc  VARCHAR(100) NOT NULL,
    status VARCHAR(100) DEFAULT 'Pending',
    PRIMARY KEY (cid),
    FOREIGN KEY (s_loc) REFERENCES surv_loc(s_loc)
);

CREATE TABLE IF NOT EXISTS survielance (
    sid        INT          NOT NULL AUTO_INCREMENT,
    s_loc      VARCHAR(100) NOT NULL,
    dos        DATE         NOT NULL,
    start_time TIME         NOT NULL,
    end_time   TIME         NOT NULL,
    with_mask  VARCHAR(20)  NOT NULL,
    without    VARCHAR(20)  NOT NULL,
    PRIMARY KEY (sid),
    FOREIGN KEY (s_loc) REFERENCES surv_loc(s_loc)
);
```

### 5a. Load seed data (optional)

To populate the database with default records for testing, run:

```bash
mysql -u <user> -p <database_name> < seed_data.sql
```

This inserts the following default data:

**login** — default password for both accounts is `Admin@123` (PBKDF2-hashed).

`INSERT IGNORE` skips any row that already exists, so the script is safe to run multiple times.

| Username | Email | Role |
|---|---|---|
| Super Admin | superadmin@maskdetector.com | Super Admin |
| Admin User | admin@maskdetector.com | Admin |

After running the seed script, log in with:

| Email | Password |
|---|---|
| superadmin@maskdetector.com | Admin@123 |
| admin@maskdetector.com | Admin@123 |

> **Important:** Change both passwords immediately after first login.

**surv_loc**

| Location |
|---|
| Main Gate |
| Canteen |
| Library |
| Parking Lot |
| Reception |

**complaint**

| Name | Mobile | Email | Location | Status |
|---|---|---|---|---|
| Ravi Kumar | 9876543210 | ravi@example.com | Main Gate | Pending |
| Priya Sharma | 9123456780 | priya@example.com | Canteen | Pending |
| Arjun Mehta | 9988776655 | arjun@example.com | Library | Surviellance done successfully |

**survielance**

| Location | Date | Start | End | With Mask | Without Mask |
|---|---|---|---|---|---|
| Main Gate | 2024-01-15 | 09:00 | 09:30 | 87.5 % | 12.5 % |
| Canteen | 2024-01-15 | 12:00 | 12:45 | 72.0 % | 28.0 % |
| Library | 2024-01-16 | 10:00 | 10:20 | 95.0 % | 5.0 % |
| Parking Lot | 2024-01-16 | 08:30 | 09:00 | 60.0 % | 40.0 % |
| Reception | 2024-01-17 | 11:00 | 11:30 | 100.0 % | 0.0 % |

### 5b. Create your own Super Admin

To create a Super Admin with your own credentials (instead of the seed defaults):

```bash
python3 setup_admin.py
```

This hashes the password using PBKDF2-HMAC-SHA256 before storing it.

### 6. Run the application

**Step 1 — Activate the virtual environment**

```bash
# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

**Step 2 — Make sure MySQL is running and your `.env` is filled in**

```env
DB_HOST=your_database_host
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_NAME=your_database_name

EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
```

**Step 3 — Set up the database (first time only)**

```bash
# Create tables
mysql -u <user> -p <database_name> < database_setup.sql

# Load default records
mysql -u <user> -p <database_name> < seed_data.sql
```

**Step 4 — Start the app**

```bash
python3 main.py
```

**Step 5 — Log in**

Use the default credentials from the seed data:

| Email | Password |
|---|---|
| superadmin@maskdetector.com | Admin@123 |
| admin@maskdetector.com | Admin@123 |

> Change both passwords immediately after first login via the Forgot Password flow.

---

## How It Works

### Mask Detection Logic

The app uses two OpenCV Haar Cascade classifiers:

- **Face cascade** (`front1.xml`) — detects faces in the video frame
- **Mouth cascade** (`haarcascade_mcs_mouth.xml`) — detects exposed mouth/lips

Detection rules applied per frame:

| Condition | Result |
|---|---|
| No face detected (normal or B&W image) | No person present |
| Face detected in B&W only (not normal) | Wearing mask (white mask edge case) |
| Face detected, no mouth detected | Wearing mask |
| Face detected, mouth detected within face bounds | Not wearing mask |

### User Roles

| Role | Access |
|---|---|
| **Super Admin** | Full access — add/remove admins, view complaints, run surveillance. Requires OTP on login. |
| **Admin** | Can run surveillance sessions and view history only. |

### Surveillance Session Flow

1. Select a surveillance location from the dropdown
2. Click **Start** — webcam activates, mask detection begins, counts are tracked live
3. Click **Stop** — session ends, masked/unmasked percentages are calculated and a pie chart is shown
4. Click **Save Surveillance** — session data is written to the database

---

## SMS Notifications

SMS sending is stubbed out in `sms_sending.py`. To enable it, integrate a provider such as [Twilio](https://www.twilio.com):

```bash
pip install twilio
```

Then update `sms_sending.py` with your Twilio credentials.

---

## Security Notes

- Credentials are stored in `.env` and loaded at runtime — never commit `.env` to version control
- All database queries use parameterised statements (no SQL injection)
- Super Admin login requires OTP verification via email

---

## License

[Apache 2.0](LICENSE)
