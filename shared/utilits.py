import re

from django.template.loader import render_to_string
from rest_framework.exceptions import ValidationError
import threading
from django.core.mail import EmailMessage

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
PHONE_REGEX = re.compile(r"^\+?1?\d{9,15}$")

def check_email_or_phone(email_phone_number):
    if re.fullmatch(EMAIL_REGEX, email_phone_number):
        sign_type = 'email'
    elif re.fullmatch(PHONE_REGEX, email_phone_number):
        sign_type = 'phone'
    else:
        context = {
            "status": "error",
            'message': 'email yoki telefon raqam noto\'g\'ri kiritildi'
        }
        raise ValidationError(context)

    return sign_type



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