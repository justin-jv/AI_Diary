from django.urls import path
from . import views

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

    path('delete-diary/<int:diary_id>/', views.delete_diary, name='delete_diary')
]
