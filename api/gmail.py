import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
import os
from django.core.mail.backends.base import BaseEmailBackend

# When see google.auth.exceptions:
# 1. Delete the file token.json
# 2. Create a new credentials and replace the file credentials.json with it.
# https://console.cloud.google.com/apis/credentials
# 3. Run `python gmail.py` to reauthenticate

CURR_DIR = os.path.dirname(os.path.abspath(__file__))

SERVICE_ACCOUNT_EMAIL = os.environ.get("SERVICE_ACCOUNT_EMAIL")

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://mail.google.com/"]


class Gmail:
    def __init__(self):
        self.service = self.init_service()

    def init_service(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(f"{CURR_DIR}/token.json"):
            creds = Credentials.from_authorized_user_file(
                f"{CURR_DIR}/token.json", SCOPES
            )
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    f"{CURR_DIR}/credentials.json", SCOPES
                )
                creds = flow.run_local_server(bind_addr="0.0.0.0", port=8001)
            # Save the credentials for the next run
            with open(f"{CURR_DIR}/token.json", "w") as token:
                token.write(creds.to_json())

        service = build("gmail", "v1", credentials=creds)
        return service

    def example(self):
        """Shows basic usage of the Gmail API.
        Lists the user's Gmail labels.
        """
        try:
            # Call the Gmail API
            results = self.service.users().labels().list(userId="me").execute()
            labels = results.get("labels", [])

            if not labels:
                print("No labels found.")
                return
            print("Labels:")
            for label in labels:
                print(label["name"])

        except HttpError as error:
            # TODO(developer) - Handle errors from gmail API.
            print(f"An error occurred: {error}")
        finally:
            # Close httplib2 connections, not the service object.
            self.service.close()


class GmailBackend(BaseEmailBackend):
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.service = self.init_service()

    def init_service(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(f"{CURR_DIR}/token.json"):
            creds = Credentials.from_authorized_user_file(
                f"{CURR_DIR}/token.json", SCOPES
            )
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    f"{CURR_DIR}/credentials.json", SCOPES
                )
                creds = flow.run_local_server(bind_addr="0.0.0.0", port=8001)
            # Save the credentials for the next run
            with open(f"{CURR_DIR}/token.json", "w") as token:
                token.write(creds.to_json())

        service = build("gmail", "v1", credentials=creds)
        return service

    def send_message(self, email_message):
        message = email_message.message()
        raw_message = {"raw": base64.urlsafe_b64encode(message.as_bytes()).decode()}
        try:
            self.service.users().messages().send(
                userId="me", body=raw_message
            ).execute()
        except HttpError as error:
            # TODO(developer) - Handle errors from gmail API.
            print(f"An error occurred: {error}")
            return False

        return True

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        if not isinstance(self.service, Resource):
            return 0

        num_sent = 0
        for message in email_messages:
            num_sent += self.send_message(message)

        # Close httplib2 connections, not the service object.
        self.service.close()

        return num_sent


if __name__ == "__main__":
    gmail = Gmail()
    gmail.example()
