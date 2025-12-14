"""
Views for homepage and NGO/Helper listings
"""

from django.shortcuts import render
from django.db.models import Q
from django.http import JsonResponse
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


def ajax_search(request):
    """
    AJAX endpoint for SMART relevance-based search
    Shows exact matches first, then related results
    """
    query = request.GET.get('search', '').strip()
    
    if not query:
        # Return all if no query
        verified_individuals = IndividualHelper.objects.filter(user__status='verified')
        verified_ngos = NGO.objects.filter(user__status='verified')
        
        results = []
        for individual in verified_individuals:
            results.append({
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
                'score': 0
            })
        
        for ngo in verified_ngos:
            results.append({
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
                'score': 0
            })
        
        return JsonResponse({
            'results': results,
            'count': len(results),
            'query': query
        })
    
    # Smart search with relevance scoring
    query_lower = query.lower()
    query_words = query_lower.split()
    
    def calculate_relevance_score(text, name_text=''):
        """
        Calculate relevance score:
        - Exact match = 100 points
        - Starts with query = 80 points  
        - Contains all words = 60 points
        - Partial word match = 20 points per word
        - Name match = bonus 50 points
        """
        text_lower = text.lower()
        name_lower = name_text.lower()
        score = 0
        
        # HIGHEST PRIORITY: Exact match
        if query_lower == text_lower or f" {query_lower} " in f" {text_lower} " or text_lower.startswith(query_lower + " ") or text_lower.endswith(" " + query_lower):
            score += 100
        
        # HIGH PRIORITY: Text starts with query
        elif text_lower.startswith(query_lower):
            score += 80
        
        # MEDIUM PRIORITY: Contains query as phrase
        elif query_lower in text_lower:
            score += 60
        
        # Check individual words
        words_found = sum(1 for word in query_words if word in text_lower)
        score += words_found * 20
        
        # BONUS: Match in name/organization
        if query_lower in name_lower:
            score += 50
        
        return score
    
    # Get all verified profiles
    all_individuals = IndividualHelper.objects.filter(user__status='verified')
    all_ngos = NGO.objects.filter(user__status='verified')
    
    results = []
    
    # Score and filter individuals
    for individual in all_individuals:
        location_score = calculate_relevance_score(individual.location, individual.full_name)
        name_score = calculate_relevance_score(individual.full_name)
        animals_score = calculate_relevance_score(individual.animals_helped)
        
        max_score = max(location_score, name_score, animals_score)
        
        # Only include if there's some match (score > 0)
        if max_score > 0:
            results.append({
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
                'score': max_score
            })
    
    # Score and filter NGOs
    for ngo in all_ngos:
        location_score = calculate_relevance_score(ngo.location, ngo.ngo_name)
        name_score = calculate_relevance_score(ngo.ngo_name)
        services_score = calculate_relevance_score(ngo.services_provided)
        
        max_score = max(location_score, name_score, services_score)
        
        # Only include if there's some match
        if max_score > 0:
            results.append({
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
                'score': max_score
            })
    
    # Sort by relevance score (highest first)
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # Remove score from output (internal use only)
    for result in results:
        del result['score']
    
    return JsonResponse({
        'results': results,
        'count': len(results),
        'query': query
    })


def privacy_policy(request):
    """Privacy Policy page"""
    return render(request, 'listings/privacy-policy.html')
