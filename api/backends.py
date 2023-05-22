from django.core.mail.backends.base import BaseEmailBackend
from .tasks import send_gmail


class GmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        for email_message in email_messages:
            # Cannot pass email_message due to kombu.exceptions.EncodeError
            message = email_message.message()
            send_gmail.delay(message)

        return 0
