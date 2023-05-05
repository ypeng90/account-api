from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os.path

CURR_DIR = os.path.dirname(os.path.abspath(__file__))

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


if __name__ == "__main__":
    gmail = Gmail()
    gmail.example()
