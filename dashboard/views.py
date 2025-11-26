"""
Views for individual and NGO dashboards
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import IndividualHelper, NGO


@login_required
def individual_dashboard(request):
    """
    Dashboard for individual helpers
    """
    if request.user.user_type != 'individual':
        messages.error(request, 'Access denied')
        return redirect('listings:home')
    
    try:
        profile = request.user.individual_profile
    except IndividualHelper.DoesNotExist:
        messages.error(request, 'Profile not found')
        return redirect('listings:home')
    
    context = {
        'profile': profile,
        'user': request.user,
        'animals_list': profile.get_animals_list(),  # ✅ ADD THIS LINE
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
    
    try:
        profile = request.user.ngo_profile
    except NGO.DoesNotExist:
        messages.error(request, 'Profile not found')
        return redirect('listings:home')
    
    context = {
        'profile': profile,
        'user': request.user,
        'services_list': profile.get_services_list(),  # ✅ ADD THIS LINE
    }
    
    return render(request, 'dashboard/ngo.html', context)
