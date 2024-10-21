import os
from django.shortcuts import render
from .google_auth import authenticate
from django.http import HttpResponse, HttpResponseRedirect
from googleapiclient.discovery import build
import base64
from email.message import EmailMessage
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from .forms import GoogleAuthForm
from google_auth_oauthlib.flow import InstalledAppFlow
from django.urls import reverse

# Allow insecure transport for local development
# os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Create your views here.

def index(request):
    return HttpResponse("welcome. You're at the mailer index.")

def test_auth(request):
    credentials_path = request.session.get('credentials_path')
    if not credentials_path:
        return HttpResponse("Credentials not found in session.")
    
    token_path = 'token.json'
    creds = authenticate(credentials_path, token_path, request.build_absolute_uri(reverse('oauth2callback')))
    if creds:
        return HttpResponse("google auth successful")
    
    return HttpResponse("google auth failed")

def send_email_with_tracking(service):
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
        tracking_url = f'https://744c-2409-40c4-ea-2e14-8c66-1b52-a5fe-1819.ngrok-free.app/track-open?email={recipient}'
        email_body_with_pixel = f'{body_text}<br><img src="{tracking_url}" width="100" height="100">'

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

def track_open(request):
    email = request.GET.get('email', 'unknown')
    print(f"Email opened by: {email}")

    image_path = os.path.join(os.path.dirname(__file__), 'atomic_habits.png')

    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()

    return HttpResponse(image_data, content_type="image/png")

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
        return None

def send_email(request):
    credentials_path = request.session.get('credentials_path')
    if not credentials_path:
        return HttpResponse("Credentials not found in session.")
    
    token_path = 'token.json'
    try:
        creds = authenticate(credentials_path, token_path, request.build_absolute_uri(reverse('oauth2callback')))
        service = build('gmail', 'v1', credentials=creds)
        draft = send_email_with_tracking(service)
        if draft:
            draft_id = draft["id"]
            gmail_send_draft(service, draft_id)
            return HttpResponse("Email sent successfully")
        else:
            return HttpResponse("Failed to send email")

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")

def google_auth(request):
    if request.method == 'POST':
        form = GoogleAuthForm(request.POST, request.FILES)
        if form.is_valid():
            credentials_file = request.FILES['credentials_file']
            scopes = form.cleaned_data['scopes'].split(',')

            # Save the uploaded credentials file temporarily
            credentials_path = 'temp_credentials.json'
            with open(credentials_path, 'wb') as f:
                for chunk in credentials_file.chunks():
                    f.write(chunk)

            # Perform OAuth flow
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, scopes)
            flow.redirect_uri = request.build_absolute_uri(reverse('oauth2callback'))
            authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')

            # Save the state in the session
            request.session['state'] = state
            request.session['credentials_path'] = credentials_path

            return HttpResponseRedirect(authorization_url)
    else:
        form = GoogleAuthForm()

    return render(request, 'google_auth.html', {'form': form})

def oauth2callback(request):
    state = request.session['state']
    credentials_path = request.session['credentials_path']

    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, scopes=None, state=state)
    flow.redirect_uri = request.build_absolute_uri(reverse('oauth2callback'))
    flow.fetch_token(authorization_response=request.build_absolute_uri())

    creds = flow.credentials

    # Save the credentials for future use
    token_path = 'token.json'
    with open(token_path, 'w') as token:
        token.write(creds.to_json())

    # Clean up temporary credentials file
    os.remove(credentials_path)

    return HttpResponse("Google authentication successful")