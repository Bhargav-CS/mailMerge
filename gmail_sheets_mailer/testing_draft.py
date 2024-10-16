import base64
from email.message import EmailMessage

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials

def gmail_create_draft(service):
    """Create and insert a draft email.
    Print the returned draft's message and id.
    Returns: Draft object, including draft id and message meta data.
    """
    try:
        message = EmailMessage()

        # Define email details
        recipient = "patkibhargav@gmail.com"
        sender = "bhargavpatki@gmail.com"
        subject = "Automated draft with tracking pixel"
        body_text = "This is an automated draft mail with a tracking pixel."

        # Add tracking pixel URL in the email body
        tracking_url = f'https://5eb4-2409-40c4-e8-8554-cce8-7a14-bb68-56ac.ngrok-free.app/track-open?email={recipient}'
        email_body_with_pixel = f'{body_text}<br><img src="{tracking_url}" width="1" height="1" style="display:none;">'

        # Set the email content to HTML
        message.set_content(email_body_with_pixel, subtype='html')

        message["To"] = recipient
        message["From"] = sender
        message["Subject"] = subject

        # Encode the message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {"message": {"raw": encoded_message}}
        # pylint: disable=E1101
        draft = (
            service.users()
            .drafts()
            .create(userId="me", body=create_message)
            .execute()
        )

        print(f'Draft id: {draft["id"]}\nDraft message: {draft["message"]}')
        return draft

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

def gmail_send_draft(service, draft_id):
    """Send the draft email.
    """
    try:
        # pylint: disable=E1101
        sent_message = (
            service.users()
            .drafts()
            .send(userId="me", body={"id": draft_id})
            .execute()
        )

        print(f'Sent message id: {sent_message["id"]}\nSent message: {sent_message}')

    except HttpError as error:
        print(f"An error occurred: {error}")

def main():
    SCOPES = ['https://www.googleapis.com/auth/gmail.compose']
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    try:
        # create gmail api client
        service = build("gmail", "v1", credentials=creds)

        # Create the draft
        draft = gmail_create_draft(service)
        if draft:
            # Send the draft
            gmail_send_draft(service, draft["id"])

    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == "__main__":
    main()