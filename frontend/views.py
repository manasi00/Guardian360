from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from . import sql
import os
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth import login, logout
from .middlewares import auth, guest
from django.contrib.auth.models import User
from django.conf import settings


@auth
def index(request):
    conn = sql.create_connection()
    cur = conn.cursor()
    rows = cur.execute("SELECT * FROM url ORDER BY url_id DESC").fetchall()
    if rows:
        video = rows[0][1]
        mode = "sql"
        if 'media/video/' in video:
            video = os.path.basename(video)
            mode = "default"
    else:
        video = "manasi.mp4"
        mode = "default"
    return render(request, 'index.html', {"video": video, "mode": mode})


@auth
def recordings(request):
    rec_arr = [rec for rec in os.listdir('media/video') if rec.endswith('.mp4') or rec.endswith('.avc1')]
    return render(request, 'recordings.html', {'rec_arr': rec_arr})

@auth
def events(request):
    conn = sql.create_connection()
    cur = conn.cursor()
    rows = cur.execute("SELECT * FROM events WHERE exited_at IS NOT NULL").fetchall()
    return render(request, 'events.html', {'rows': rows})

@auth
def view_video(request, video):
    video_path = video
    return render(request, 'view_video.html', {'video_path': video_path})


@csrf_exempt
@auth
def add_url(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        if url:
            sql.add_url(url)
            return redirect('index')
    return render(request, 'index.html')

@guest
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Initialize the form to use for error handling
        form = AuthenticationForm(request, data=request.POST)
        
        if username and password:
            if username == settings.STATIC_USERNAME and password == settings.STATIC_PASSWORD:
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    # Create a new user if not exist
                    user = User(username=username)
                    user.set_password(password)  # set_password is used to handle hashed passwords
                    user.save()
                
                login(request, user)  # Log the user in
                return redirect('index')  # Redirect to the index page
            else:
                form.add_error(None, "Invalid username or password")
        else:
            form.add_error(None, "Please enter both username and password")
    else:
        form = AuthenticationForm()

    return render(request, 'auth/login.html', {'form': form})

@auth
def setting(request):
    conn = sql.create_connection()
    cur = conn.cursor()
    rows = cur.execute("SELECT * FROM url ORDER BY url_id DESC").fetchall()
    if rows:
        url = rows[0][1]
    else:
        url = None
    return render(request, 'setting.html', {"url": url})


@auth
def logout_view(request):
    logout(request)
    return redirect('login')

