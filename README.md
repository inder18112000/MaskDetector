# Mask Detector

A desktop surveillance application that uses a webcam and **YOLOv8 deep learning** to detect whether people are wearing face masks in real time. Includes admin authentication with email OTP (2FA), a public complaint portal, and a surveillance dashboard with session reporting.

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup](#setup)
- [Environment Variables](#environment-variables)
- [Detection Pipeline](#detection-pipeline)
- [Dashboard Camera Lifecycle](#dashboard-camera-lifecycle)
- [Authentication Flow](#authentication-flow)
- [Responsive Layout](#responsive-layout)
- [User Roles](#user-roles)
- [Dependencies](#dependencies)
- [Security Notes](#security-notes)

---

## Tech Stack

| Layer | Technology |
|---|---|
| GUI | Python Tkinter (Canvas-based custom widgets for macOS compatibility) |
| Computer Vision | OpenCV (`opencv-python`) |
| Deep Learning | YOLOv8 via `ultralytics` |
| Model Source | HuggingFace Hub (`huggingface_hub`) |
| Database | MySQL via `PyMySQL` |
| Email / OTP | Gmail SMTP SSL (port 465) with `certifi` |
| Charts | Matplotlib embedded in Tkinter |
| Image Loading | Pillow (`PIL`) |
| Config | `python-dotenv` (`.env` file) |

---

## Project Structure

```
MaskDetector/
├── main.py                          Entry point
├── otp.py                           OTP email sender (Gmail SMTP SSL)
├── sms_sending.py                   SMS notification stub
├── connection.py                    Database connection helper
├── .env                             Credentials — DO NOT commit
├── .env.example                     Credential template
├── requirements.txt                 All dependencies
├── database_setup.sql               Schema creation script
├── seed_data.sql                    Default locations, users, sample data
├── setup_admin.py                   Admin account creation utility
│
├── app/
│   ├── state.py                     Global session state (result, mode, vid)
│   ├── theme.py                     Colors, fonts, StyledButton (Canvas-based)
│   ├── paths.py                     Asset path constants (Images, Cascades, Models)
│   ├── security.py                  PBKDF2-HMAC-SHA256 hash / verify
│   ├── db/
│   │   ├── users.py                 Admin user CRUD
│   │   ├── complaints.py            Complaint CRUD
│   │   ├── locations.py             Surveillance location CRUD
│   │   └── surveillance.py          Session record CRUD
│   ├── camera/
│   │   ├── video_capture.py         OpenCV capture wrapper (BGR → RGB)
│   │   └── mask_detector.py         YOLOv8 inference (MASKED / UNMASKED)
│   └── views/
│       ├── login.py                 Login + OTP 2FA (Super Admin)
│       ├── dashboard_light.py       Main dashboard (light theme)
│       ├── dashboard_dark.py        Main dashboard (dark theme)
│       ├── admin_add.py             Add admin with OTP verification
│       ├── admin_view.py            View / edit / delete admins
│       ├── complaint.py             Public complaint submission form
│       ├── complaint_show.py        View complaints (filterable by location)
│       ├── forgot_password.py       Password reset via OTP
│       └── surveillance_history.py  View past surveillance sessions
│
└── assets/
    ├── images/                      UI backgrounds and icons
    ├── cascades/                    Haar XML files (legacy, unused)
    └── models/
        └── face_mask.pt             YOLOv8 model (~22 MB, auto-downloaded on first run)
```

---

## Setup

### 1. Clone and create virtual environment

```bash
git clone <repo-url>
cd MaskDetector
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your database and Gmail credentials
```

### 4. Set up the database

```bash
mysql -u <user> -p < database_setup.sql
mysql -u <user> -p MaskDetector < seed_data.sql
```

### 5. Create admin account

```bash
python setup_admin.py
```

### 6. Run

```bash
python main.py
```

> **First run note:** On the first click of **Start Camera**, the YOLOv8 model (~22 MB) is automatically downloaded from HuggingFace and saved to `assets/models/face_mask.pt`. All subsequent runs load it from disk instantly.

### macOS camera permission

On first launch macOS will request camera access. If the camera fails to open, go to:
**System Settings → Privacy & Security → Camera** and enable access for your terminal or Python app.

---

## Environment Variables

| Variable | Description |
|---|---|
| `DB_HOST` | MySQL host (e.g. `localhost`) |
| `DB_USER` | MySQL username |
| `DB_PASSWORD` | MySQL password |
| `DB_NAME` | Database name (e.g. `MaskDetector`) |
| `EMAIL_ADDRESS` | Gmail address used to send OTP emails |
| `EMAIL_PASSWORD` | Gmail App Password (16-char, requires 2FA enabled on the account) |

**Getting a Gmail App Password:**
1. Enable 2-Step Verification on your Google account
2. Go to **Google Account → Security → App Passwords**
3. Generate a password for "Mail"
4. Paste the 16-character code as `EMAIL_PASSWORD`

---

## Detection Pipeline

### Frame Capture — `app/camera/video_capture.py`

```
OpenCV VideoCapture (BGR)
        ↓
  cv2.cvtColor(BGR → RGB)
        ↓
  Returns (ret, rgb_frame)
```

Frames are always **RGB** when they leave this module.

### Mask Detection — `app/camera/mask_detector.py`

**Model:** `Nma/Face-Mask-yolov8` (YOLOv8, public on HuggingFace, ~22 MB)

| Class ID | Label | Status |
|---|---|---|
| 0 | `face` | UNMASKED |
| 1 | `face_masked` | MASKED |

```
rgb_frame (H × W × 3)
       ↓
  _get_model()            ← lazy-loads on first call; auto-downloads if missing
       ↓
  YOLO.predict(conf=0.45)
       ↓
  for each detection box:
      cls == 1  →  MASKED   (green box, "Mask On")
      cls == 0  →  UNMASKED (red box,   "No Mask!")
       ↓
  returns [(x, y, w, h, status), ...], has_face: bool
```

Detections below **0.45 confidence** are discarded.

**Auto-download logic** (runs once on first Start, then cached):

```
assets/models/face_mask.pt exists?
    YES → load directly with YOLO()
    NO  → hf_hub_download("Nma/Face-Mask-yolov8", "best.pt")
          → copy to assets/models/face_mask.pt
          → load with YOLO()
```

---

## Dashboard Camera Lifecycle

### Start Camera

```
start_camera()
    ├── destroy previous chart widget (if any)
    ├── reset masked / unmasked counters to 0
    ├── MyVideoCapture().startVideo(camera_index)
    │       ├── success   → create camera Frame + Canvas inside main_frame
    │       └── ValueError → showerror dialog, re-enable Start button (no crash)
    └── begin update() loop every 15 ms
```

### Per-frame loop (`update()`)

```
update()
    ├── flag == False → return (loop stopped)
    ├── cap.get_frame() → (ret, rgb_frame)
    ├── ret == False or img is None → schedule next tick, return
    ├── cv2.resize(850 × 600) + cv2.flip (mirror effect)
    ├── mask_detector.detect(rgb_frame) → detections, has_face
    ├── no face → draw "No face detected" overlay
    └── per detection (x, y, w, h, status):
            MASKED   → green rectangle + "Mask On"   label above box
            UNMASKED → red rectangle   + "No Mask!"  label above box
            increment self.masked or self.unmasked counter
```

### Stop Camera

```
stop_camera()
    ├── camera_release() + canvas.destroy() + camera frame.destroy()
    ├── flag = False  (halts update loop immediately)
    ├── compute masked % and unmasked % from counters
    └── render donut pie chart via FigureCanvasTkAgg in main_frame
```

---

## Authentication Flow

```
Login page
    ├── All roles     → email + password → PBKDF2-HMAC-SHA256 verify
    └── Super Admin   → OTP sent via Gmail SMTP SSL (port 465, certifi SSL context)
                      → Toplevel modal dialog for OTP entry
                      → secrets.compare_digest() (constant-time, timing-safe)
                      → destroy OTP window first, then main login window
                      → open dashboard
```

Passwords stored as `salt_hex:hash_hex`
(PBKDF2-HMAC-SHA256, 100 000 iterations, column `VARCHAR(200)`).

---

## Responsive Layout

```
root window
├── nav bar      (TOP,    fill=X,              height=50)  ← Add/View Admins, Complaints, History
├── bottom bar   (BOTTOM, fill=X,              height=60)  ← Add Location, Dark/Light Mode, Logout
├── sidebar      (LEFT,   fill=Y,              width=300)  ← User info, form fields, camera controls
└── main_frame   (LEFT,   fill=BOTH, expand=True)          ← Camera feed / compliance chart
```

- `minsize(900, 600)` prevents layout breakage on small windows
- Login card centered with `relx=0.5, rely=0.5, anchor=CENTER`
- No hardcoded `place(x, y)` coordinates — fully `pack`-based

---

## User Roles

| Role | Permissions |
|---|---|
| **Super Admin** | Full access — manage admins, view complaints, run surveillance, add locations. Requires OTP on every login. |
| **Admin** | Can run surveillance sessions and view history only. Add Admin / View Admins / Add Location buttons are disabled. |

---

## Surveillance Session Flow

1. Select a surveillance **location** from the dropdown
2. Enter **camera index** (default `0` for built-in webcam)
3. Click **▶ Start** — webcam activates, YOLOv8 detection begins, counters update live
4. Click **■ Stop** — session ends, masked/unmasked % calculated, donut chart shown
5. Click **💾 Save Surveillance** — session record written to database, complaint statuses updated

---

## SMS Notifications

SMS sending is stubbed out in `sms_sending.py`. To enable it, integrate a provider such as Twilio:

```bash
pip install twilio
```

Then update `sms_sending.py` with your Twilio `account_sid`, `auth_token`, and phone numbers.

---

## Dependencies

| Package | Purpose |
|---|---|
| `opencv-python` | Camera capture, frame resize/flip, bounding box drawing |
| `Pillow` | JPEG login background loading, PIL → Tkinter image conversion |
| `pymysql` | MySQL database connection |
| `matplotlib` | Donut pie chart after each surveillance session |
| `python-dotenv` | `.env` credential loading at runtime |
| `certifi` | SSL certificates for Gmail SMTP on macOS |
| `ultralytics` | YOLOv8 inference engine |
| `huggingface_hub` | Auto-download of `face_mask.pt` model on first run |
| `dill` | Model serialisation (auto-installed by ultralytics) |

---

## Security Notes

- Credentials stored in `.env` and loaded at runtime — **never commit `.env`**
- All database queries use parameterised statements — no SQL injection
- Passwords hashed with PBKDF2-HMAC-SHA256 (100k iterations + unique salt per password)
- OTP comparison uses `secrets.compare_digest()` — constant-time, resistant to timing attacks
- Super Admin login always requires OTP regardless of password correctness
