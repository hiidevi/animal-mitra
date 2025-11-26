"""
Views for individual and NGO dashboards
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from accounts.models import IndividualHelper, NGO, PendingProfileUpdate


@login_required
def individual_dashboard(request):
    """
    Dashboard for individual helpers
    """
    if request.user.user_type != 'individual':
        messages.error(request, 'Access denied')
        return redirect('listings:home')
    
    # Check if deletion requested
    if request.user.status == 'deletion_requested':
        messages.error(request, '🗑️ Your account deletion is pending. You cannot access your dashboard.')
        logout(request)
        return redirect('listings:home')
    
    try:
        profile = request.user.individual_profile
    except IndividualHelper.DoesNotExist:
        messages.error(request, 'Profile not found')
        return redirect('listings:home')
    
    context = {
        'profile': profile,
        'user': request.user,
        'animals_list': profile.get_animals_list(),
    }
    
    return render(request, 'dashboard/individual.html', context)


@login_required
def ngo_dashboard(request):
    """
    Dashboard for NGOs
    """
    if request.user.user_type != 'ngo':
        messages.error(request, 'Access denied')
        return redirect('listings:home')
    
    # Check if deletion requested
    if request.user.status == 'deletion_requested':
        messages.error(request, '🗑️ Your account deletion is pending. You cannot access your dashboard.')
        logout(request)
        return redirect('listings:home')
    
    try:
        profile = request.user.ngo_profile
    except NGO.DoesNotExist:
        messages.error(request, 'Profile not found')
        return redirect('listings:home')
    
    context = {
        'profile': profile,
        'user': request.user,
        'services_list': profile.get_services_list(),
    }
    
    return render(request, 'dashboard/ngo.html', context)


@login_required
def update_profile(request):
    """
    Handle profile update request (requires re-approval)
    """
    if request.method == 'POST':
        user = request.user
        
        # Store pending changes
        if user.user_type == 'individual':
            pending_data = {
                'full_name': request.POST.get('full_name'),
                'mobile': request.POST.get('mobile'),
                'location': request.POST.get('location'),
                'whatsapp': request.POST.get('whatsapp', ''),
                'instagram': request.POST.get('instagram', ''),
                'animals_helped': request.POST.get('animals_helped'),
                'about': request.POST.get('about'),
            }
        else:  # NGO
            pending_data = {
                'ngo_name': request.POST.get('ngo_name'),
                'emergency_contact': request.POST.get('emergency_contact'),
                'location': request.POST.get('location'),
                'whatsapp': request.POST.get('whatsapp', ''),
                'instagram': request.POST.get('instagram', ''),
                'telegram': request.POST.get('telegram', ''),
                'services_provided': request.POST.get('services_provided'),
                'operating_hours': request.POST.get('operating_hours', ''),
            }
        
        # Save or update pending changes
        PendingProfileUpdate.objects.update_or_create(
            user=user,
            defaults={'data': pending_data}
        )
        
        # Change status to pending_update
        user.status = 'pending_update'
        user.save()
        
        messages.success(
            request,
            '✏️ Profile changes submitted! Your updates will be reviewed by admin within 24 hours. You will receive an email notification once approved.'
        )
        
        if user.user_type == 'individual':
            return redirect('dashboard:individual')
        else:
            return redirect('dashboard:ngo')
    
    return redirect('dashboard:individual')


@login_required
def request_deletion(request):
    """
    User requests account deletion
    """
    if request.method == 'POST':
        user = request.user
        user.status = 'deletion_requested'
        user.save()
        
        messages.warning(
            request,
            '🗑️ Account deletion request received. Your account will be reviewed and deleted within 24 hours. You will not be able to login during this period.'
        )
        
        # Logout user immediately
        logout(request)
        return redirect('listings:home')
    
    return redirect('dashboard:individual')
