"""
URL patterns for admin panel
"""
from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.admin_panel_view, name='panel'),
    path('approve/<int:user_id>/', views.approve_registration, name='approve'),
    path('reject/<int:user_id>/', views.reject_registration, name='reject'),
    path('deactivate/<int:user_id>/', views.deactivate_user, name='deactivate'),
]