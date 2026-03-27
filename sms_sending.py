import logging

logger = logging.getLogger(__name__)

def send_sms(phone_number):
    """
    Send an SMS notification to the given phone number.

    This is a stub. To enable SMS, integrate a provider such as Twilio:
      pip install twilio
      from twilio.rest import Client
      client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
      client.messages.create(body="...", from_=os.getenv("TWILIO_FROM"), to=phone_number)
    """
    logger.info("SMS stub called for number: %s (not sent — configure a provider in sms_sending.py)", phone_number)
