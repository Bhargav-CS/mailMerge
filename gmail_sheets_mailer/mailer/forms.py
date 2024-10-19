from django import forms

class GoogleAuthForm(forms.Form):
    credentials_file = forms.FileField(label='Upload your credentials.json file')
    scopes = forms.CharField(label='Scopes', max_length=255, initial='https://www.googleapis.com/auth/gmail.send')