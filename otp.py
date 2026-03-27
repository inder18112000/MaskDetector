import smtplib
import ssl
import string
import random
import os
import certifi
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

load_dotenv()

class OTPSendError(Exception):
    pass


def send(i):
    email_address = os.getenv("EMAIL_ADDRESS")
    email_password = os.getenv("EMAIL_PASSWORD")

    if not email_address or not email_password:
        raise OTPSendError(
            "EMAIL_ADDRESS or EMAIL_PASSWORD not set in .env"
        )

    msg = MIMEMultipart()
    res = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    message = "Hello,\n    Your OTP for admin login is: " + res
    msg["From"] = email_address
    msg["To"] = str(i)
    msg["Subject"] = "One Time Password — Mask Detector"
    msg.attach(MIMEText(message))

    ctx = ssl.create_default_context(cafile=certifi.where())
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx, timeout=10) as s:
            s.login(email_address, email_password)
            s.sendmail(email_address, str(i), msg.as_string())
    except smtplib.SMTPAuthenticationError:
        raise OTPSendError(
            "Gmail authentication failed.\n\n"
            "To fix:\n"
            "1. Enable 2-Step Verification on your Google account\n"
            "2. Go to myaccount.google.com/apppasswords\n"
            "3. Generate an App Password and paste it in .env as EMAIL_PASSWORD"
        )
    except Exception as e:
        raise OTPSendError(f"Failed to send OTP email: {e}")

    return res
