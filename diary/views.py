from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import DiaryEntry
from textblob import TextBlob
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password


# Create your views here.

CustomUser = get_user_model()

# Home Page
@login_required(login_url='login')
def home(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('login')

    total_diaries = DiaryEntry.objects.filter(user=user).count()
    last_created = DiaryEntry.objects.filter(user=user).order_by('-created_at').first()
    latest_diaries = DiaryEntry.objects.filter(user=user).order_by('-created_at')[:5]
    diary_status = "Active" if not user.is_diary_blocked else "Blocked"

    context = {
        'total_diaries': total_diaries,
        'last_created': last_created,
        'diary_status': diary_status,
        'latest_diaries': latest_diaries,
    }
    return render(request, 'diary/home.html',context)

# Signup Page
def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('signup')
        user = CustomUser.objects.create_user(username=username, email=email, password=password)
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
            if hasattr(user, 'is_blocked') and user.is_blocked:
                messages.error(request, "Your account has been blocked by the admin.")
                return redirect('login')
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid Credentials.")
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


# Admin User List
@staff_member_required(login_url='admin_login')
def admin_user_list(request):
    users = CustomUser.objects.filter(is_staff=False)
    return render(request, 'diary/admin_user_list.html', {'users': users})

# Admin User Block/Unblock
@staff_member_required(login_url='admin_login')
def toggle_user_block(request, user_id):
    user = CustomUser.objects.get(id = user_id)
    user.is_blocked = not user.is_blocked
    user.save()
    return redirect('admin_user_list')

# Admin User Diary Block/Unblock
@staff_member_required(login_url='admin_login')
def toggle_diary_block(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    user.is_diary_blocked = not user.is_diary_blocked
    user.save()
    return redirect('admin_user_list')


# Create Diary
@login_required
def create_diary(request):
    if request.user.is_diary_blocked:
        messages.error(request, "You are restricted from creating diary entries.")
        return redirect('home')
    
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
    if request.user.is_diary_blocked:
        messages.error(request, "You are restricted from viewing your diaries.")
        return redirect('home')
    
    diaries = DiaryEntry.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'diary/diary_list.html', {'diaries': diaries})

# Diary Detail View
@login_required
def diary_detail(request, diary_id):
    if request.user.is_diary_blocked:
        messages.error(request, "You are restricted from accessing diary entries.")

    diary = DiaryEntry.objects.get(id=diary_id, user=request.user)
    return render(request, 'diary/diary_detail.html', {'diary':diary})

# Edit Diary Entry
@login_required
def edit_diary(request, diary_id):
    if request.user.is_diary_blocked:
        messages.error(request, "You are restricted from editing diary entries.")
        return redirect('home')
    
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


# Forgot Password
def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = request.build_absolute_uri(f'/reset-password/{uid}/{token}/')

            subject = 'Reset Your Password'
            message = render_to_string('diary/password_reset_email.html',{
                'user': user,
                'reset_url': reset_url
            })

            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
            messages.success(request, 'Password reset link has been sent to your email.')
            return redirect('forgot_password')
        except CustomUser.DoesNotExist:
            messages.error(request, 'Email Not Found.')
            return redirect('forgot_password')
        
    return render(request, 'diary/forgot_password.html')

# Reset Password
def reset_password_view(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            if password != confirm_password:
                messages.error(request, 'Passwords do not match')
                return redirect(request.path)

            user.password = make_password(password)
            user.save()
            messages.success(request, 'Password has been reset. You can now log in.')
            return redirect('login')
        
        return render(request, 'diary/reset_password.html')
    else:
        messages.error(request, 'Invalid or expired link')
        return redirect('forgot_password')