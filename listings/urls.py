"""
URL patterns for homepage and listings
"""
from django.urls import path
from . import views

app_name = 'listings'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('api/search/', views.ajax_search, name='ajax_search'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
]
