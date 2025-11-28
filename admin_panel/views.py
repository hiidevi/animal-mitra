"""
Views for admin panel with email notifications
Fixed: Async email sending to prevent timeouts
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from accounts.models import User, IndividualHelper, NGO, PendingProfileUpdate
from threading import Thread
import logging

# Setup logger for debugging
logger = logging.getLogger(__name__)


def send_approval_email_async(user_email, user_type_display):
    """
    Send approval email in background thread (non-blocking)
    
    Problem: send_mail() blocks the request = timeout on Render
    Solution: Run in separate thread = immediate response
    """
    def send_email():
        subject = '🎉 Your Animal Mitra Account Has Been Approved!'
        message = f"""
Dear {user_email},

Congratulations! Your Animal Mitra account has been approved by our admin team.

You can now log in and access your dashboard:
https://animal-mitra.onrender.com/accounts/login/

Account Details:
- Email: {user_email}
- Type: {user_type_display}
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
                [user_email],
                fail_silently=False,
            )
            logger.info(f'✅ Approval email sent successfully to {user_email}')
        except Exception as e:
            logger.error(f'❌ Email failed for {user_email}: {str(e)}')
    
    # Run email sending in background thread
    thread = Thread(target=send_email)
    thread.daemon = True  # Thread dies when main program exits
    thread.start()


def send_update_approval_email_async(user_email):
    """
    Send profile update approval email (async)
    """
    def send_email():
        subject = '✅ Your Profile Update Has Been Approved!'
        message = f"""
Dear {user_email},

Your profile update request has been approved by our admin team.

Your updated information is now live on Animal Mitra.

Login to view: https://animal-mitra.onrender.com/accounts/login/

Best regards,
Animal Mitra Team
        """
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user_email],
                fail_silently=False,
            )
            logger.info(f'✅ Update approval email sent to {user_email}')
        except Exception as e:
            logger.error(f'❌ Email failed for {user_email}: {str(e)}')
    
    thread = Thread(target=send_email)
    thread.daemon = True
    thread.start()


def send_deletion_cancelled_email_async(user_email):
    """
    Send deletion cancelled email (async)
    """
    def send_email():
        subject = '✅ Account Deletion Cancelled'
        message = f"""
Dear {user_email},

Your account deletion request has been cancelled by our admin team.

Your account is still active and you can continue using Animal Mitra.

Login: https://animal-mitra.onrender.com/accounts/login/

Best regards,
Animal Mitra Team
        """
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user_email],
                fail_silently=False,
            )
            logger.info(f'✅ Cancellation email sent to {user_email}')
        except Exception as e:
            logger.error(f'❌ Email failed for {user_email}: {str(e)}')
    
    thread = Thread(target=send_email)
    thread.daemon = True
    thread.start()


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
    
    # Get pending updates and deletion requests
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
    
    FIXED: Email now sends asynchronously (non-blocking)
    - No more timeouts!
    - Immediate response to admin
    - Email sends in background
    """
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('listings:home')
    
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        user.status = 'verified'
        user.save()
        
        # Send email asynchronously (non-blocking)
        send_approval_email_async(user.email, user.get_user_type_display())
        
        # Immediate success message (don't wait for email)
        messages.success(request, f'✅ {user.email} approved! Notification email is being sent.')
        logger.info(f'Admin approved user: {user.email}')
    
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
        logger.info(f'Admin rejected user: {user.email}')
    
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
        logger.info(f'Admin edited user: {user.email}')
    
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
        logger.info(f'Admin deleted user: {email}')
    
    return redirect('admin_panel:panel')


@login_required
def approve_update(request, user_id):
    """
    Approve profile update changes
    
    FIXED: Async email sending
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
            
            # Send email asynchronously
            send_update_approval_email_async(user.email)
            
            messages.success(request, f'✅ Profile update approved for {user.email}! Notification being sent.')
            logger.info(f'Admin approved update for: {user.email}')
            
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
            logger.info(f'Admin rejected update for: {user.email}')
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
        logger.info(f'Admin approved deletion: {email}')
    
    return redirect('admin_panel:panel')


@login_required
def cancel_deletion(request, user_id):
    """
    Cancel deletion request (restore account)
    
    FIXED: Async email sending
    """
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('listings:home')
    
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        user.status = 'verified'  # Restore to verified
        user.save()
        
        # Send email asynchronously
        send_deletion_cancelled_email_async(user.email)
        
        messages.success(request, f'✅ Deletion cancelled for {user.email}. Account restored. Notification being sent.')
        logger.info(f'Admin cancelled deletion for: {user.email}')
    
    return redirect('admin_panel:panel')
