"""
Views for user registration, login, and logout
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import IndividualRegistrationForm, NGORegistrationForm
from .models import User

def register_view(request):
    """
    Handle both individual and NGO registration
    """
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        
        if user_type == 'individual':
            form = IndividualRegistrationForm(request.POST)
        elif user_type == 'ngo':
            form = NGORegistrationForm(request.POST, request.FILES)
        else:
            messages.error(request, 'Please select a user type')
            return redirect('accounts:register')
        
        if form.is_valid():
            user = form.save()
            messages.success(
                request, 
                'Thank you for registering! We will verify your information and approve within 24 hours. '
                'You will receive an email once approved.'
            )
            return redirect('accounts:login')
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = None
    
    context = {
        'individual_form': IndividualRegistrationForm(),
        'ngo_form': NGORegistrationForm(),
    }
    return render(request, 'accounts/register.html', context)


def login_view(request):
    """
    Handle user login with user type selection
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_type = request.POST.get('user_type')
        
        # Authenticate user
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            # Check if user type matches
            if user.user_type != user_type:
                messages.error(request, f'This account is not registered as {user_type}')
                return redirect('accounts:login')
            
            # Check if account is verified
            if user.status == 'pending':
                messages.warning(
                    request, 
                    'Your account is pending verification. You will be able to login once admin approves your registration.'
                )
                return redirect('accounts:login')
            
            if user.status == 'rejected':
                messages.error(request, 'Your account has been rejected. Please contact admin for details.')
                return redirect('accounts:login')
            
            # Login successful
            login(request, user)
            
            # Redirect based on user type
            if user.user_type == 'individual':
                return redirect('dashboard:individual')
            elif user.user_type == 'ngo':
                return redirect('dashboard:ngo')
            elif user.user_type == 'admin':
                return redirect('admin_panel:panel')
        else:
            messages.error(request, 'Invalid email or password')
    
    return render(request, 'accounts/login.html')


@login_required
def logout_view(request):
    """
    Handle user logout
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('listings:home')