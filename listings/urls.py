"""
URL patterns for homepage and listings
"""
from django.urls import path
from . import views

app_name = 'listings'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('search/', views.search_view, name='search'),
]