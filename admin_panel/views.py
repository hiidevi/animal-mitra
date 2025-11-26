"""
Views for custom admin panel
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from accounts.models import User, IndividualHelper, NGO

@login_required
def admin_panel_view(request):
    """
    Main admin panel dashboard
    """
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied. Admin only.')
        return redirect('listings:home')
    
    # Get pending registrations
    pending_users = User.objects.filter(status='pending')
    
    # Get approved users
    verified_users = User.objects.filter(status='verified')
    
    # Statistics
    stats = {
        'pending_count': pending_users.count(),
        'verified_count': verified_users.count(),
        'total_count': User.objects.exclude(user_type='admin').count(),
        'total_views': sum([
            sum([i.profile_views for i in IndividualHelper.objects.all()]),
            sum([n.profile_views for n in NGO.objects.all()])
        ]),
    }
    
    # Prepare pending registrations with profiles
    pending_list = []
    for user in pending_users:
        if user.user_type == 'individual':
            try:
                profile = user.individual_profile
                pending_list.append({
                    'user': user,
                    'profile': profile,
                    'type': 'individual',
                })
            except:
                pass
        elif user.user_type == 'ngo':
            try:
                profile = user.ngo_profile
                pending_list.append({
                    'user': user,
                    'profile': profile,
                    'type': 'ngo',
                })
            except:
                pass
    
    # Prepare verified listings
    verified_list = []
    for user in verified_users:
        if user.user_type == 'individual':
            try:
                profile = user.individual_profile
                verified_list.append({
                    'user': user,
                    'profile': profile,
                    'type': 'individual',
                })
            except:
                pass
        elif user.user_type == 'ngo':
            try:
                profile = user.ngo_profile
                verified_list.append({
                    'user': user,
                    'profile': profile,
                    'type': 'ngo',
                })
            except:
                pass
    
    context = {
        'stats': stats,
        'pending_list': pending_list,
        'verified_list': verified_list,
    }
    
    return render(request, 'admin_panel/panel.html', context)


@login_required
def approve_registration(request, user_id):
    """
    Approve a pending registration
    """
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('listings:home')
    
    user = get_object_or_404(User, id=user_id)
    user.status = 'verified'
    user.save()
    
    # Send email notification (optional)
    # send_mail(
    #     'Account Approved - Animal Mitra',
    #     f'Your account has been approved! You can now login at http://animalmitra.com/login',
    #     'admin@animalmitra.com',
    #     [user.email],
    # )
    
    messages.success(request, f'{user.email} has been approved and is now live on the website!')
    return redirect('admin_panel:panel')


@login_required
def reject_registration(request, user_id):
    """
    Reject a pending registration
    """
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('listings:home')
    
    user = get_object_or_404(User, id=user_id)
    user.status = 'rejected'
    user.save()
    
    messages.warning(request, f'{user.email} has been rejected')
    return redirect('admin_panel:panel')


@login_required
def deactivate_user(request, user_id):
    """
    Deactivate a verified user
    """
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('listings:home')
    
    user = get_object_or_404(User, id=user_id)
    user.status = 'rejected'
    user.save()
    
    messages.success(request, f'User has been deactivated')
    return redirect('admin_panel:panel')