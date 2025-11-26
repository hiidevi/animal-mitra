from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('individual/', views.individual_dashboard, name='individual'),
    path('ngo/', views.ngo_dashboard, name='ngo'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('request-deletion/', views.request_deletion, name='request_deletion'),
]
