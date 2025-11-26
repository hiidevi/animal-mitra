"""
URLs for accounts app
"""
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),  # ← FIXED: Line 10 (was register_view)
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
]
