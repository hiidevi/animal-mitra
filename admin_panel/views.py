"""
Views for admin panel
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import User, IndividualHelper, NGO


@login_required
def admin_panel(request):
    """
    Main admin panel view
    """
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied - Admin only')
        return redirect('listings:home')
    
    # Get all users with different statuses
    all_users = User.objects.all()
    pending_users = all_users.filter(status='pending').select_related('individual_profile', 'ngo_profile')
    
    context = {
        'total_users': all_users.count(),
        'pending_count': all_users.filter(status='pending').count(),
        'verified_count': all_users.filter(status='verified').count(),
        'rejected_count': all_users.filter(status='rejected').count(),
        'pending_users': pending_users,
    }
    
    return render(request, 'admin_panel/panel.html', context)


@login_required
def approve_user(request, user_id):
    """
    Approve a pending user
    """
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('listings:home')
    
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        user.status = 'verified'
        user.save()
        messages.success(request, f'{user.email} has been approved!')
    
    return redirect('admin_panel:panel')


@login_required
def reject_user(request, user_id):
    """
    Reject a pending user
    """
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('listings:home')
    
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        user.status = 'rejected'
        user.save()
        messages.warning(request, f'{user.email} has been rejected.')
    
    return redirect('admin_panel:panel')
