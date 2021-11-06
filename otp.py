import smtplib
import string
import random
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send(i):
    msg = MIMEMultipart()
    res = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 6))
    message = str("Hello,\n    Your OTP for admin login id: " + str(res))
    msg["From"] ="inderjit.singh112000@gmail.com"
    msg["To"] = str(i)
    msg["Subject"] = "ONE TIME PASSWORD "
    body= MIMEText(message)
    msg.attach(body)
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login("inderjit.singh112000@gmail.com", "helloworld18")

    s.sendmail("inderjit.singh112000@gmail.com", str(i), str(msg))
    s.quit()
    return str(res)
