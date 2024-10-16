def index(request):
    return HttpResponse("Hello, world. You're at the mailer index.")

def test_auth(request):
    creds = authenticate()
    if creds:
        return HttpResponse("google auth successful")
    
    return HttpResponse("google auth failed")