# send email verify email
from django.core import mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
import datetime


class SendEmail:
    def __init__(self):
        self.from_email = 'The1App <webmaster@localhost>'

    def send_plain_email(self, subject, to, message_text, plain_message=None):
        mail.send_mail(subject, plain_message, self.from_email, [to], html_message=message_text)

    def send_attachment_email(self):
        pass