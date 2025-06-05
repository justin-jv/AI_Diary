from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import DiaryEntry
from textblob import TextBlob



# Create your views here.


# Home Page
@login_required(login_url='login')
def home(request):
    return render(request, 'diary/home.html')

# Signup Page
def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('signup')
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, 'Account created successfully')
        return redirect('login')
    return render(request, 'diary/signup.html')

# Login Page
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request,username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials")
            return redirect('login')
    return render(request, 'diary/login.html')

# Logout
def logout_view(request):
    logout(request)
    return redirect('login')

# Admin Login
def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid admin credentials')
            return redirect('admin_login')
    return render(request, 'diary/admin_login.html')

# Admin Dashboard
@staff_member_required(login_url='admin_login')
def admin_dashboard(request):
    return render(request, 'diary/admin_dashboard.html')


# Create Diary
@login_required
def create_diary(request):
    if request.method == 'POST':
        title = request.POST['title']
        content = request.POST['content']
        sentiment = TextBlob(content).sentiment.polarity
        mood = 'positive' if sentiment > 0 else 'negative' if sentiment < 0 else 'neutral'

        DiaryEntry.objects.create(user=request.user, title=title, content=content, sentiment=mood)
        messages.success(request, 'Diary entry created with mood detection!!')
        return redirect('diary_list')
    
        # Old Code before adding sentiment and mood detection

        # diary = DiaryEntry(user=request.user, title=title, content=content)
        # diary.save()
        # messages.success(request, 'Diary entry created!!')
        # return redirect('home')

    return render(request, 'diary/create_diary.html')


# Diary List View
@login_required
def diary_list(request):
    diaries = DiaryEntry.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'diary/diary_list.html', {'diaries': diaries})

# Diary Detail View
@login_required
def diary_detail(request, diary_id):
    diary = DiaryEntry.objects.get(id=diary_id, user=request.user)
    return render(request, 'diary/diary_detail.html', {'diary':diary})

# Edit Diary Entry
@login_required
def edit_diary(request, diary_id):
    diary = DiaryEntry.objects.get(id=diary_id, user=request.user)
    if request.method == 'POST':
        diary.title = request.POST['title']
        diary.content = request.POST['content']

        sentiment = TextBlob(diary.content).sentiment.polarity
        diary.sentiment = 'positive' if sentiment > 0 else 'negative' if sentiment < 0 else 'neutral'

        diary.save()
        messages.success(request, 'Diary updated Successfully!!')
        return redirect('diary_list')
    return render(request, 'diary/edit_diary.html', {'diary':diary})

# Deleting Diary Entry
@login_required
def delete_diary(request, diary_id):
    diary = DiaryEntry.objects.get(id=diary_id, user=request.user)
    diary.delete()
    messages.success(request, 'Diary Deleted Successfully!!')
    return redirect('diary_list')