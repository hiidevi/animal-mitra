"""
Views for homepage and NGO/Helper listings
"""
from django.shortcuts import render
from accounts.models import IndividualHelper, NGO, User

def home_view(request):
    """
    Homepage with all verified NGOs and helpers
    """
    # Get only verified users
    verified_individuals = IndividualHelper.objects.filter(user__status='verified')
    verified_ngos = NGO.objects.filter(user__status='verified')
    
    # Combine for display
    all_listings = []
    
    for individual in verified_individuals:
        all_listings.append({
            'type': 'individual',
            'name': individual.full_name,
            'phone': individual.mobile,
            'location': individual.location,
            'whatsapp': individual.whatsapp,
            'instagram': individual.instagram,
            'telegram': '',
            'animals': individual.get_animals_list(),
            'timing': 'Flexible',
            'verified': True,
        })
    
    for ngo in verified_ngos:
        all_listings.append({
            'type': 'ngo',
            'name': ngo.ngo_name,
            'phone': ngo.emergency_contact,
            'location': ngo.location,
            'whatsapp': ngo.whatsapp,
            'instagram': ngo.instagram,
            'telegram': ngo.telegram,
            'animals': ngo.get_services_list(),
            'timing': ngo.operating_hours or '9 AM - 6 PM',
            'verified': True,
        })
    
    context = {
        'listings': all_listings,
        'total_count': len(all_listings),
    }
    
    return render(request, 'listings/index.html', context)


def search_view(request):
    """
    Search and filter listings
    """
    query = request.GET.get('q', '')
    animal_type = request.GET.get('animal', '')
    
    # Filter logic here
    # Will implement based on search requirements
    
    return render(request, 'listings/search.html', {'query': query})

def privacy_policy(request):
    """Privacy Policy page"""
    return render(request, 'listings/privacy-policy.html')
