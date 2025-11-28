"""
Views for admin panel with email notifications
Fixed: Async email sending to prevent timeouts
Added: Rejection and deletion notifications
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from accounts.models import User, IndividualHelper, NGO, PendingProfileUpdate
from threading import Thread
import logging

logger = logging.getLogger(__name__)


def send_approval_email_async(user_email, user_type_display):
    """Send approval email in background thread (non-blocking)"""
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
        """
        
        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email], fail_silently=False)
            logger.info(f'✅ Approval email sent to {user_email}')
        except Exception as e:
            logger.error(f'❌ Email failed for {user_email}: {str(e)}')
    
    thread = Thread(target=send_email)
    thread.daemon = True
    thread.start()


def send_rejection_email_async(user_email):
    """Send account rejection email (async)"""
    def send_email():
        subject = '❌ Your Animal Mitra Registration Status'
        message = f"""
Dear {user_email},

Thank you for your interest in joining Animal Mitra.

Unfortunately, your registration request has not been approved at this time. This may be due to:
- Incomplete information
- Verification requirements not met
- Duplicate registration

If you believe this is an error or would like to reapply with updated information, please contact us at contact@animal-mitra.com

Best regards,
Animal Mitra Team
        """
        
        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email], fail_silently=False)
            logger.info(f'✅ Rejection email sent to {user_email}')
        except Exception as e:
            logger.error(f'❌ Email failed for {user_email}: {str(e)}')
    
    thread = Thread(target=send_email)
    thread.daemon = True
    thread.start()


def send_update_approval_email_async(user_email):
    """Send profile update approval email (async)"""
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
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email], fail_silently=False)
            logger.info(f'✅ Update approval email sent to {user_email}')
        except Exception as e:
            logger.error(f'❌ Email failed for {user_email}: {str(e)}')
    
    thread = Thread(target=send_email)
    thread.daemon = True
    thread.start()


def send_deletion_cancelled_email_async(user_email):
    """Send deletion cancelled email (async)"""
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
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email], fail_silently=False)
            logger.info(f'✅ Cancellation email sent to {user_email}')
        except Exception as e:
            logger.error(f'❌ Email failed for {user_email}: {str(e)}')
    
    thread = Thread(target=send_email)
    thread.daemon = True
    thread.start()


def send_account_deleted_email_async(user_email, user_name):
    """Send account deletion notification email (async)"""
    def send_email():
        subject = '⚠️ Your Animal Mitra Account Has Been Deleted'
        message = f"""
Dear {user_name or user_email},

This is to inform you that your Animal Mitra account has been permanently deleted from our system.

Account Details:
- Email: {user_email}
- Deletion Date: Today

All your information has been removed from our database. If you believe this was done in error, please contact us immediately at contact@animal-mitra.com

If you wish to register again in the future, you can do so at:
https://animal-mitra.onrender.com/accounts/register/

Thank you for being part of Animal Mitra.

Best regards,
Animal Mitra Team
        """
        
        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email], fail_silently=False)
            logger.info(f'✅ Deletion notification sent to {user_email}')
        except Exception as e:
            logger.error(f'❌ Email failed for {user_email}: {str(e)}')
    
    thread = Thread(target=send_email)
    thread.daemon = True
    thread.start()


@login_required
def admin_panel(request):
    """Main admin panel view with tabs"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied - Admin only')
        return redirect('listings:home')
    
    all_users = User.objects.exclude(user_type='admin')
    pending_users = all_users.filter(status='pending').select_related('individual_profile', 'ngo_profile')
    verified_users = all_users.filter(status='verified').select_related('individual_profile', 'ngo_profile')
    rejected_users = all_users.filter(status='rejected').select_related('individual_profile', 'ngo_profile')
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
    """Approve a pending user - FIXED: Async email sending"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('listings:home')
    
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        user.status = 'verified'
        user.save()
        
        # Send email asynchronously (non-blocking)
        send_approval_email_async(user.email, user.get_user_type_display())
        
        messages.success(request, f'✅ {user.email} approved! Notification email is being sent.')
        logger.info(f'Admin approved user: {user.email}')
    
    return redirect('admin_panel:panel')


@login_required
def reject_user(request, user_id):
    """Reject a pending user - NEW: Sends rejection email"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('listings:home')
    
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        user_email = user.email
        user.status = 'rejected'
        user.save()
        
        # Send rejection email
        send_rejection_email_async(user_email)
        
        messages.warning(request, f'{user_email} has been rejected. Notification sent.')
        logger.info(f'Admin rejected user: {user_email}')
    
    return redirect('admin_panel:panel')


@login_required
def edit_user(request, user_id):
    """Edit user information (admin direct edit)"""
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
    """Delete user permanently (from verified/rejected lists)"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('listings:home')
    
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        
        # Save user info before deletion
        user_email = user.email
        user_name = None
        
        # Get user's name before deletion
        if user.user_type == 'individual':
            try:
                user_name = user.individual_profile.full_name
            except:
                pass
        elif user.user_type == 'ngo':
            try:
                user_name = user.ngo_profile.ngo_name
            except:
                pass
        
        # Send notification BEFORE deleting
        send_account_deleted_email_async(user_email, user_name)
        
        # Now delete the account
        user.delete()
        
        messages.success(request, f'{user_email} has been deleted permanently. Notification sent.')
        logger.info(f'Admin deleted user: {user_email}')
    
    return redirect('admin_panel:panel')


@login_required
def approve_update(request, user_id):
    """Approve profile update changes - FIXED: Async email"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('listings:home')
    
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        
        try:
            pending = user.pending_update
            
            if user.user_type == 'individual':
                profile = user.individual_profile
                for key, value in pending.data.items():
                    setattr(profile, key, value)
                profile.save()
            else:
                profile = user.ngo_profile
                for key, value in pending.data.items():
                    setattr(profile, key, value)
                profile.save()
            
            pending.delete()
            user.status = 'verified'
            user.save()
            
            send_update_approval_email_async(user.email)
            
            messages.success(request, f'✅ Profile update approved for {user.email}! Notification being sent.')
            logger.info(f'Admin approved update for: {user.email}')
            
        except PendingProfileUpdate.DoesNotExist:
            messages.error(request, 'No pending updates found.')
    
    return redirect('admin_panel:panel')


@login_required
def reject_update(request, user_id):
    """Reject profile update changes (keep old data)"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('listings:home')
    
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        
        try:
            pending = user.pending_update
            pending.delete()
            user.status = 'verified'
            user.save()
            
            messages.warning(request, f'Profile update rejected for {user.email}. Old data kept.')
            logger.info(f'Admin rejected update for: {user.email}')
        except PendingProfileUpdate.DoesNotExist:
            messages.error(request, 'No pending updates found.')
    
    return redirect('admin_panel:panel')


@login_required
def approve_deletion(request, user_id):
    """Approve and delete user account permanently - NEW: Sends deletion notification"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('listings:home')
    
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        
        # Save user info before deletion
        user_email = user.email
        user_name = None
        
        # Get user's name before deletion
        if user.user_type == 'individual':
            try:
                user_name = user.individual_profile.full_name
            except:
                pass
        elif user.user_type == 'ngo':
            try:
                user_name = user.ngo_profile.ngo_name
            except:
                pass
        
        # Send notification BEFORE deleting
        send_account_deleted_email_async(user_email, user_name)
        
        # Now delete the account
        user.delete()
        
        messages.success(request, f'Account deleted: {user_email}. Notification sent.')
        logger.info(f'Admin approved deletion: {user_email}')
    
    return redirect('admin_panel:panel')


@login_required
def cancel_deletion(request, user_id):
    """Cancel deletion request (restore account) - FIXED: Async email"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('listings:home')
    
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        user.status = 'verified'
        user.save()
        
        send_deletion_cancelled_email_async(user.email)
        
        messages.success(request, f'✅ Deletion cancelled for {user.email}. Account restored. Notification being sent.')
        logger.info(f'Admin cancelled deletion for: {user.email}')
    
    return redirect('admin_panel:panel')
