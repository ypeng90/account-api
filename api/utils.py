import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
import os

# When see google.auth.exceptions:
# 1. Delete the file token.json
# 2. Create a new credentials and replace the file credentials.json with it.
# https://console.cloud.google.com/apis/credentials
# 3. Run `python utils.py` to reauthenticate

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

        return build("gmail", "v1", credentials=creds)

    # Passed message is acutally email_message.message() due to kombu.exceptions.EncodeError
    def send_message(self, message):
        if not isinstance(self.service, Resource):
            return False

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


def gmail_test():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    try:
        client = Gmail()
        # Call the Gmail API
        results = client.service.users().labels().list(userId="me").execute()
        labels = results.get("labels", [])

        if not labels:
            print("No labels found.")
            return

        for label in labels:
            print(label["name"])
            break
    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")
    finally:
        # Close httplib2 connections, not the service object.
        client.service.close()


if __name__ == "__main__":
    gmail_test()
