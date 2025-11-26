"""
Views for user authentication and registration
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import IndividualHelperForm, NGOForm
from .models import User, IndividualHelper, NGO


def register(request):
    """
    Handle user registration for both individuals and NGOs
    """
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        
        if user_type == 'individual':
            form = IndividualHelperForm(request.POST)
            if form.is_valid():
                # Create user account
                user = User.objects.create_user(
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password1'],
                    user_type='individual',
                    status='pending'
                )
                
                # Create individual helper profile
                IndividualHelper.objects.create(
                    user=user,
                    full_name=form.cleaned_data['full_name'],
                    mobile=form.cleaned_data['mobile'],
                    location=form.cleaned_data['location'],
                    whatsapp=form.cleaned_data.get('whatsapp', ''),
                    instagram=form.cleaned_data.get('instagram', ''),
                    animals_helped=', '.join(form.cleaned_data['animals_helped']),
                    about=form.cleaned_data['about']
                )
                
                # Success message with 24-hour notice
                messages.success(
                    request, 
                    '✅ Registration successful! Your account will be reviewed and approved by our admin team within 24 hours. You will receive an email notification once approved.'
                )
                return redirect('accounts:login')
            else:
                messages.error(request, 'Please correct the errors below.')
        
        elif user_type == 'ngo':
            form = NGOForm(request.POST, request.FILES)
            if form.is_valid():
                # Create user account
                user = User.objects.create_user(
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password1'],
                    user_type='ngo',
                    status='pending'
                )
                
                # Create NGO profile
                NGO.objects.create(
                    user=user,
                    ngo_name=form.cleaned_data['ngo_name'],
                    email=form.cleaned_data['email'],
                    emergency_contact=form.cleaned_data['emergency_contact'],
                    location=form.cleaned_data['location'],
                    whatsapp=form.cleaned_data.get('whatsapp', ''),
                    instagram=form.cleaned_data.get('instagram', ''),
                    telegram=form.cleaned_data.get('telegram', ''),
                    services_provided=', '.join(form.cleaned_data['services_provided']),
                    operating_hours=form.cleaned_data.get('operating_hours', ''),
                    certificate=form.cleaned_data.get('certificate')
                )
                
                # Success message with 24-hour notice
                messages.success(
                    request,
                    '✅ Registration successful! Your account will be reviewed and approved by our admin team within 24 hours. You will receive an email notification once approved.'
                )
                return redirect('accounts:login')
            else:
                messages.error(request, 'Please correct the errors below.')
    
    # GET request - show forms
    individual_form = IndividualHelperForm()
    ngo_form = NGOForm()
    
    context = {
        'individual_form': individual_form,
        'ngo_form': ngo_form,
    }
    
    return render(request, 'accounts/register.html', context)


def user_login(request):
    """
    Handle user login
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            if user.status == 'pending':
                messages.warning(
                    request,
                    '⏳ Your account is pending approval. Please wait for admin verification. You will receive an email once approved.'
                )
                return redirect('accounts:login')
            elif user.status == 'rejected':
                messages.error(request, '❌ Your account has been rejected. Please contact admin for more information.')
                return redirect('accounts:login')
            else:
                # User is verified
                login(request, user)
                
                # Redirect based on user type
                if user.user_type == 'admin':
                    return redirect('admin_panel:panel')
                elif user.user_type == 'individual':
                    return redirect('dashboard:individual')
                elif user.user_type == 'ngo':
                    return redirect('dashboard:ngo')
        else:
            messages.error(request, '❌ Invalid email or password.')
    
    return render(request, 'accounts/login.html')


@login_required
def user_logout(request):
    """
    Handle user logout
    """
    logout(request)
    messages.success(request, '✅ You have been logged out successfully.')
    return redirect('listings:home')
