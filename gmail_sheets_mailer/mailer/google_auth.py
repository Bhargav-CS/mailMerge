import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the environment variables
GOOGLE_CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH')
GOOGLE_TOKEN_PATH = os.getenv('GOOGLE_TOKEN_PATH')

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def authenticate():
    creds = None
    if os.path.exists(GOOGLE_TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(GOOGLE_TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(GOOGLE_CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(GOOGLE_TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
    return creds