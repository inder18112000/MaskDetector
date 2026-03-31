import smtplib
import ssl
import string
import random
import os
import time
from threading import Lock
import certifi
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.logger import get

load_dotenv()

_log = get(__name__)


class OTPSendError(Exception):
    pass


class OTPRateLimitError(OTPSendError):
    """Raised when too many OTP requests are made for the same email."""
    pass


# ── Rate limiting ─────────────────────────────────────────────────────────────
_MAX_ATTEMPTS  = 3      # max OTPs per email per window
_WINDOW_SECS   = 300    # 5-minute sliding window
_rate_lock     = Lock()
_attempts: dict = {}    # email -> list[float] of send timestamps


def _check_rate_limit(email: str) -> None:
    """Raise OTPRateLimitError if the email has exceeded the send quota."""
    email = email.lower().strip()
    now   = time.monotonic()
    with _rate_lock:
        recent = [t for t in _attempts.get(email, []) if now - t < _WINDOW_SECS]
        if len(recent) >= _MAX_ATTEMPTS:
            wait_secs = int(_WINDOW_SECS - (now - recent[0]))
            mins, secs = divmod(wait_secs, 60)
            _log.warning("OTP rate limit hit for %s (%d/%d in window)",
                         email, len(recent), _MAX_ATTEMPTS)
            raise OTPRateLimitError(
                f"Too many OTP requests.\n\n"
                f"Please wait {mins}m {secs}s before requesting another OTP."
            )
        recent.append(now)
        _attempts[email] = recent
# ─────────────────────────────────────────────────────────────────────────────


def send(i, purpose: str = "reset"):
    """
    Send a one-time password email.

    Parameters
    ----------
    i       : recipient email address
    purpose : "login"  — 2FA verification after Super Admin sign-in
              "reset"  — password reset flow (default)
    """
    _check_rate_limit(str(i))

    email_address = os.getenv("EMAIL_ADDRESS")
    email_password = os.getenv("EMAIL_PASSWORD")

    if not email_address or not email_password:
        raise OTPSendError(
            "EMAIL_ADDRESS or EMAIL_PASSWORD not set in .env"
        )

    res = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    _log.info("OTP sending to %s for purpose=%s", i, purpose)

    if purpose == "login":
        subject      = "Login Verification OTP — Mask Detector"
        header_color = "#1e7e34"
        header_title = "Two-Factor Login Verification"
        body_text    = (
            "A sign-in attempt was made on your <strong>Mask Detector</strong> "
            "Super Admin account. Use the OTP below to complete your login."
        )
        security_note = (
            "🔒 &nbsp;Do not share this OTP with anyone.<br>"
            "⚠️ &nbsp;If you did not attempt to log in, secure your account immediately."
        )
        plain = (
            f"Mask Detector — Login Verification\n\n"
            f"Your login OTP is: {res}\n\n"
            f"Enter this code to complete your Super Admin sign-in.\n"
            f"Do not share it with anyone.\n\n"
            f"If you did not attempt to log in, secure your account immediately.\n\n"
            f"— Mask Detector Security Team"
        )
    elif purpose == "verify":
        subject      = "Admin Email Verification — Mask Detector"
        header_color = "#ff6b35"
        header_title = "Verify Admin Email"
        body_text    = (
            "An admin account is being created with this email address. "
            "Use the OTP below to verify and complete setup."
        )
        security_note = (
            "🔒 &nbsp;Do not share this OTP with anyone.<br>"
            "⚠️ &nbsp;If you did not expect this, please contact your Super Admin."
        )
        plain = (
            f"Mask Detector — Admin Email Verification\n\n"
            f"Your verification OTP is: {res}\n\n"
            f"Enter this code to verify the email address and complete admin account setup.\n"
            f"Do not share it with anyone.\n\n"
            f"If you did not expect this, please contact your Super Admin.\n\n"
            f"— Mask Detector Security Team"
        )
    else:
        subject      = "Password Reset OTP — Mask Detector"
        header_color = "#1a73e8"
        header_title = "Password Reset Request"
        body_text    = (
            "We received a request to reset your <strong>Mask Detector</strong> "
            "admin password. Use the OTP below to proceed."
        )
        security_note = (
            "🔒 &nbsp;Do not share this OTP with anyone.<br>"
            "⚠️ &nbsp;If you did not request a password reset, please ignore this email."
        )
        plain = (
            f"Mask Detector — Password Reset\n\n"
            f"Your password reset OTP is: {res}\n\n"
            f"Enter this code in the app to reset your password.\n"
            f"Do not share it with anyone.\n\n"
            f"If you did not request this, please ignore this email.\n\n"
            f"— Mask Detector Security Team"
        )

    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f4f6f9;font-family:Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f6f9;padding:40px 0;">
    <tr><td align="center">
      <table width="480" cellpadding="0" cellspacing="0"
             style="background:#ffffff;border-radius:10px;overflow:hidden;
                    box-shadow:0 2px 12px rgba(0,0,0,0.08);">

        <!-- Header -->
        <tr>
          <td style="background:{header_color};padding:28px 40px;text-align:center;">
            <p style="margin:0;font-size:11px;color:rgba(255,255,255,0.7);letter-spacing:2px;
                      text-transform:uppercase;">Mask Detector</p>
            <h1 style="margin:8px 0 0;font-size:22px;color:#ffffff;font-weight:700;">
              {header_title}
            </h1>
          </td>
        </tr>

        <!-- Body -->
        <tr>
          <td style="padding:36px 40px 24px;">
            <p style="margin:0 0 16px;font-size:15px;color:#444;">Hi,</p>
            <p style="margin:0 0 24px;font-size:15px;color:#444;line-height:1.6;">
              {body_text}
              It is valid for <strong>one use only</strong>.
            </p>

            <!-- OTP Box -->
            <div style="background:#f0f4ff;border:2px dashed {header_color};border-radius:8px;
                        padding:24px;text-align:center;margin:0 0 28px;">
              <p style="margin:0 0 6px;font-size:12px;color:#888;letter-spacing:1px;
                         text-transform:uppercase;">Your One-Time Password</p>
              <p style="margin:0;font-size:38px;font-weight:700;letter-spacing:10px;
                         color:{header_color};">{res}</p>
            </div>

            <p style="margin:0 0 8px;font-size:13px;color:#888;line-height:1.6;">
              {security_note}
            </p>
          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td style="background:#f9fafb;border-top:1px solid #e8eaed;
                     padding:18px 40px;text-align:center;">
            <p style="margin:0;font-size:12px;color:#aaa;">
              Mask Detector &nbsp;|&nbsp; Surveillance Management System<br>
              This is an automated email — please do not reply.
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""

    msg = MIMEMultipart("alternative")
    msg["From"]    = email_address
    msg["To"]      = str(i)
    msg["Subject"] = subject
    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html, "html"))

    ctx = ssl.create_default_context(cafile=certifi.where())
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx, timeout=10) as s:
            s.login(email_address, email_password)
            s.sendmail(email_address, str(i), msg.as_string())
        _log.info("OTP sent successfully to %s", i)
    except smtplib.SMTPAuthenticationError:
        _log.error("Gmail SMTP authentication failed for sender %s", email_address)
        raise OTPSendError(
            "Gmail authentication failed.\n\n"
            "To fix:\n"
            "1. Enable 2-Step Verification on your Google account\n"
            "2. Go to myaccount.google.com/apppasswords\n"
            "3. Generate an App Password and paste it in .env as EMAIL_PASSWORD"
        )
    except Exception as e:
        _log.exception("OTP send failed to %s: %s", i, e)
        raise OTPSendError(f"Failed to send OTP email: {e}")

    return res
