"""
URL patterns for user dashboards
"""
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('individual/', views.individual_dashboard, name='individual'),
    path('ngo/', views.ngo_dashboard, name='ngo'),
]