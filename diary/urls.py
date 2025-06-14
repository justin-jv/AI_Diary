from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('',views.home, name='home'),
    path('signup/',views.signup_view,name = 'signup'),
    path('login/', views.login_view, name='login'),
    path('logout/',views.logout_view, name = 'logout'),

    # Admin urls
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Create Directory
    path('create-diary/', views.create_diary, name='create_diary'),


    # Diary List
    path('my-diaries/', views.diary_list, name='diary_list'),


    path('diary/<int:diary_id>/', views.diary_detail, name='diary_detail'),


    path('edit-diary/<int:diary_id>/', views.edit_diary, name='edit_diary'),

    path('delete-diary/<int:diary_id>/', views.delete_diary, name='delete_diary'),

    # Admin User Management
    path('admin-panel/users/', views.admin_user_list, name='admin_user_list'),
    path('admin-panel/users/block/<int:user_id>/', views.toggle_user_block, name='toggle_user_block'),
    path('admin-panel/users/diary-block/<int:user_id>/',views.toggle_diary_block, name='toggle_diary_block'),

    # Password Reset Urls
    path('reset-password/', auth_views.PasswordResetView.as_view(template_name='diary/reset_password.html'), name='password_reset'),
    path('reset-password-sent/', auth_views.PasswordResetDoneView.as_view(template_name='diary/reset_password_sent.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='diary/reset_password_confirm.html'), name='password_reset_confirm'),
    path('reset-password-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='diary/reset_password_complete.html'), name='password_reset_complete'),
]
