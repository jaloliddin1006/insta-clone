import re

from django.template.loader import render_to_string
from rest_framework.exceptions import ValidationError
import threading
from django.core.mail import EmailMessage
import phonenumbers
from decouple import config
from twilio.rest import Client

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
PHONE_REGEX = re.compile(r"^\+?998?\d{9,15}$")
USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_.-]+$")

def check_email_or_phone(email_phone_number):
    if re.fullmatch(EMAIL_REGEX, email_phone_number):
        sign_type = 'email'
    elif re.match(PHONE_REGEX, email_phone_number):
        sign_type = 'phone'
    else:
        context = {
            "status": "error",
            'message': 'email yoki telefon raqam noto\'g\'ri kiritildi'
        }
        raise ValidationError(context)

    return sign_type

def check_user_type(user_input):
    if re.match(EMAIL_REGEX, user_input):
        user_input = 'email'
    elif re.match(PHONE_REGEX, user_input):
        user_input = 'phone'
    elif re.match(USERNAME_REGEX, user_input):
        user_input = 'username'
    else:
        context = {
            "status": "error",
            'message': 'login noto\'g\'ri kiritildi'
        }
        raise ValidationError(context)
    return user_input

class EmailThreading(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()

class Email:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['subject'],
            body=data['body'],
            to=[data['to_email']]
        )
        if data.get('content_type') == "html":
            email.content_subtype = "html"
        EmailThreading(email).start()

def send_mail_code(email, code):
    html_content = render_to_string(
        template_name='email/authentication/activate_account.html',
        context={'code': code}
    )
    Email.send_email({
        'subject': "Instagram tashdiqlash uchun ro'yxatdan o'tihs",
        'body': html_content,
        'to_email': email,
        'content_type': 'html'
    })


def send_phone_code(phone, code):
    account_sid = config('TWILIO_ACCOUNT_SID')
    auth_token = config('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=f"Sizning tasdiqlash kodingiz: {code}",
        from_="+998932977419", # config('TWILIO_PHONE_NUMBER')
        to=f"{phone}"
    )