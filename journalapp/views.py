from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from .models import entry
from django.utils import timezone
from django.conf import settings
import requests
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str 
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import HttpResponse



class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user.is_active)
        )
account_activation_token = TokenGenerator()

# Create your views here.
def login1(request):
    if request.method == 'POST':
        username = request.POST.get('uname') 
        password1 = request.POST.get('pwd') 
        user = authenticate(username=username, password=password1)
        userobj=User.objects.get(username=username)

        if user is not None:
            login(request, user)
            return redirect('/home')
        else:
            if userobj and not userobj.is_active:
                messages.error(request,"Please, verify your account")
            else:
                messages.error(request, 'Invalid login credentials')
    return render(request, 'login.html')

def signup1(request):
    if request.method == 'POST':
        uname1 = request.POST.get('uname')
        pwd1 = request.POST.get('pwd')
        repwd1 = request.POST.get('repwd')
        email= request.POST.get('email')
        
        if pwd1 != repwd1:
            messages.error(request, "Passwords do not match")
            return redirect('/signup')
        
        if User.objects.filter(username=uname1).exists():
            messages.error(request, 'Username is already taken')
            return redirect('/signup')
        
        if pwd1 and repwd1:
            user = User.objects.create_user(username=uname1, password=pwd1,email=email,is_active=False)
            user.save()
            current_site = get_current_site(request)
            subject = 'Activate Your Account'
            message = render_to_string('activate_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
            
            messages.success(request, "Registration successful ")
            messages.success(request, "Waiting for verification")
            return render(request, 'registration_pending.html')
        
    return render(request, 'signup.html')

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('home')  # Redirect to the homepage or another page
    else:
        return HttpResponse('Activation link is invalid!')

def home(request):
    a = entry.objects.filter(user=request.user)
    return render(request,'home.html',{'data':a})

def create_post(request):
    if request.method == 'POST':
        note= request.POST.get('notes')
        emotion=analyze_emotion(note)
        if emotion != None:
            arr=[]
            for i in emotion:
                arr.append((i,emotion[i]))
            arr.sort(key=lambda x:x[1],reverse=True)
            entry.objects.create(user=request.user,notes=note,emotion=arr[0][0])
        else:
            entry.objects.create(user=request.user,notes=note)
        return redirect('home')
    return render(request, 'notes.html')


def edit(request,id):
    a = entry.objects.get(id=id)
    
    if request.method == 'POST':
        a.notes=request.POST.get('notes')
        a.isEdited = True  # Mark the post as edited
        a.edited_at = timezone.now()  # Set the edit timestamp
        a.save()  # Save the updated post
        return redirect('/home')
    
    return render(request, 'edit.html', {'data': a})

def delete(request, id):
    del_obj = entry.objects.get(id=id)
    del_obj.delete()
    
    return redirect('/home')

def analyze_emotion(text):

    if text=="":
        return None
    
    # Make a request to the text-to-emotion API
    api_key = settings.API_KEY  # Store your API key in settings.py
    url = 'https://api.apilayer.com/text_to_emotion'
    
    headers = {
        'apikey': api_key,
        'Content-Type': 'application/json'
    }
    
    data = {
        'text': text
    }
        
    response = requests.post(url, headers=headers, json=data)
    
    # Check if the response was successful
    if response.status_code == 200:
        emotion_result = response.json()  # Parse the JSON response
    else:
        emotion_result = None
        print("api error:",response.status_code)

    return emotion_result