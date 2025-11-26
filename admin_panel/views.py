"""
Views for admin panel with email notifications
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from accounts.models import User, IndividualHelper, NGO, PendingProfileUpdate


def send_approval_email(user):
    """
    Send email notification when user is approved
    """
    subject = '🎉 Your Animal Mitra Account Has Been Approved!'
    message = f"""
Dear {user.email},

Congratulations! Your Animal Mitra account has been approved by our admin team.

You can now log in and access your dashboard:
https://yourdomain.com/accounts/login/

Account Details:
- Email: {user.email}
- Type: {user.get_user_type_display()}
- Status: Verified ✓

Thank you for joining Animal Mitra! Together, we can make a difference for animals in need.

Best regards,
Animal Mitra Team

---
Note: If you need to update your information, please log in to your dashboard.
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False


def send_update_approval_email(user):
    """
    Send email when profile update is approved
    """
    subject = '✅ Your Profile Update Has Been Approved!'
    message = f"""
Dear {user.email},

Your profile update request has been approved by our admin team.

Your updated information is now live on Animal Mitra.

Login to view: https://yourdomain.com/accounts/login/

Best regards,
Animal Mitra Team
    """
    
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False


def send_deletion_cancelled_email(user):
    """
    Send email when deletion is cancelled
    """
    subject = '✅ Account Deletion Cancelled'
    message = f"""
Dear {user.email},

Your account deletion request has been cancelled by our admin team.

Your account is still active and you can continue using Animal Mitra.

Login: https://yourdomain.com/accounts/login/

Best regards,
Animal Mitra Team
    """
    
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False


@login_required
def admin_panel(request):
    """
    Main admin panel view with tabs
    """
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied - Admin only')
        return redirect('listings:home')
    
    # Get all users with different statuses
    all_users = User.objects.exclude(user_type='admin')
    pending_users = all_users.filter(status='pending').select_related('individual_profile', 'ngo_profile')
    verified_users = all_users.filter(status='verified').select_related('individual_profile', 'ngo_profile')
    rejected_users = all_users.filter(status='rejected').select_related('individual_profile', 'ngo_profile')
    
    # New: Get pending updates and deletion requests
    pending_updates = all_users.filter(status='pending_update').select_related('individual_profile', 'ngo_profile', 'pending_update')
    deletion_requests = all_users.filter(status='deletion_requested').select_related('individual_profile', 'ngo_profile')
    
    context = {
        'total_users': all_users.count(),
        'pending_count': pending_users.count(),
        'verified_count': verified_users.count(),
        'rejected_count': rejected_users.count(),
        'pending_users': pending_users,
        'verified_users': verified_users,
        'rejected_users': rejected_users,
        'pending_updates': pending_updates,
        'pending_updates_count': pending_updates.count(),
        'deletion_requests': deletion_requests,
        'deletion_requests_count': deletion_requests.count(),
    }
    
    return render(request, 'admin_panel/panel.html', context)


@login_required
def approve_user(request, user_id):
    """
    Approve a pending user and send email notification
    """
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('listings:home')
    
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        user.status = 'verified'
        user.save()
        
        # Send email notification
        email_sent = send_approval_email(user)
        
        if email_sent:
            messages.success(request, f'{user.email} has been approved! Notification email sent.')
        else:
            messages.success(request, f'{user.email} has been approved! (Email notification failed)')
    
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


@login_required
def edit_user(request, user_id):
    """
    Edit user information (admin direct edit)
    """
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('listings:home')
    
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        
        if user.user_type == 'individual':
            profile = user.individual_profile
            profile.full_name = request.POST.get('full_name')
            profile.mobile = request.POST.get('mobile')
            profile.location = request.POST.get('location')
            profile.whatsapp = request.POST.get('whatsapp', '')
            profile.instagram = request.POST.get('instagram', '')
            profile.animals_helped = request.POST.get('animals_helped')
            profile.about = request.POST.get('about')
            profile.save()
        else:
            profile = user.ngo_profile
            profile.ngo_name = request.POST.get('ngo_name')
            profile.email = request.POST.get('email')
            profile.emergency_contact = request.POST.get('emergency_contact')
            profile.location = request.POST.get('location')
            profile.whatsapp = request.POST.get('whatsapp', '')
            profile.instagram = request.POST.get('instagram', '')
            profile.telegram = request.POST.get('telegram', '')
            profile.services_provided = request.POST.get('services_provided')
            profile.operating_hours = request.POST.get('operating_hours', '')
            profile.save()
        
        messages.success(request, f'Information updated for {user.email}')
    
    return redirect('admin_panel:panel')


@login_required
def delete_user(request, user_id):
    """
    Delete user permanently (and their profile)
    """
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('listings:home')
    
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        email = user.email
        user.delete()  # Cascade delete will remove profile too
        messages.success(request, f'{email} has been deleted permanently.')
    
    return redirect('admin_panel:panel')


@login_required
def approve_update(request, user_id):
    """
    Approve profile update changes
    """
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('listings:home')
    
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        
        try:
            pending = user.pending_update
            
            # Apply changes to actual profile
            if user.user_type == 'individual':
                profile = user.individual_profile
                for key, value in pending.data.items():
                    setattr(profile, key, value)
                profile.save()
            else:  # NGO
                profile = user.ngo_profile
                for key, value in pending.data.items():
                    setattr(profile, key, value)
                profile.save()
            
            # Delete pending update and change status back to verified
            pending.delete()
            user.status = 'verified'
            user.save()
            
            # Send email notification
            email_sent = send_update_approval_email(user)
            
            if email_sent:
                messages.success(request, f'Profile update approved for {user.email}! Notification sent.')
            else:
                messages.success(request, f'Profile update approved for {user.email}!')
        except PendingProfileUpdate.DoesNotExist:
            messages.error(request, 'No pending updates found.')
    
    return redirect('admin_panel:panel')


@login_required
def reject_update(request, user_id):
    """
    Reject profile update changes (keep old data)
    """
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('listings:home')
    
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        
        try:
            pending = user.pending_update
            pending.delete()  # Discard changes
            user.status = 'verified'  # Back to verified
            user.save()
            
            messages.warning(request, f'Profile update rejected for {user.email}. Old data kept.')
        except PendingProfileUpdate.DoesNotExist:
            messages.error(request, 'No pending updates found.')
    
    return redirect('admin_panel:panel')


@login_required
def approve_deletion(request, user_id):
    """
    Approve and delete user account permanently
    """
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('listings:home')
    
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        email = user.email
        user.delete()  # Permanently delete
        messages.success(request, f'Account deleted: {email}')
    
    return redirect('admin_panel:panel')


@login_required
def cancel_deletion(request, user_id):
    """
    Cancel deletion request (restore account)
    """
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('listings:home')
    
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        user.status = 'verified'  # Restore to verified
        user.save()
        
        # Send email notification
        email_sent = send_deletion_cancelled_email(user)
        
        if email_sent:
            messages.success(request, f'Deletion cancelled for {user.email}. Account restored. Notification sent.')
        else:
            messages.success(request, f'Deletion cancelled for {user.email}. Account restored.')
    
    return redirect('admin_panel:panel')
