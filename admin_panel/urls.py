from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.admin_panel, name='panel'),
    path('approve/<int:user_id>/', views.approve_user, name='approve_user'),
    path('reject/<int:user_id>/', views.reject_user, name='reject_user'),
    path('edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('delete/<int:user_id>/', views.delete_user, name='delete_user'),
    
    # NEW: Profile update management
    path('approve-update/<int:user_id>/', views.approve_update, name='approve_update'),
    path('reject-update/<int:user_id>/', views.reject_update, name='reject_update'),
    
    # NEW: Deletion request management
    path('approve-deletion/<int:user_id>/', views.approve_deletion, name='approve_deletion'),
    path('cancel-deletion/<int:user_id>/', views.cancel_deletion, name='cancel_deletion'),
]
