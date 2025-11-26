"""
Forms for user registration (Individual and NGO)
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, IndividualHelper, NGO


class IndividualHelperForm(UserCreationForm):  # ← CHANGED: Line 10 (was IndividualRegistrationForm)
    """
    Registration form for individual helpers
    """
    full_name = forms.CharField(
        max_length=200, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'John Doe'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your.email@example.com'})
    )
    mobile = forms.CharField(
        max_length=15, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 98765 43210'})
    )
    location = forms.CharField(
        max_length=200, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sector 15, Faridabad'})
    )
    whatsapp = forms.CharField(
        max_length=15, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 98765 43210'})
    )
    instagram = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '@your_handle'})
    )
    
    ANIMAL_CHOICES = (
        ('dogs', 'Dogs'),
        ('cats', 'Cats'),
        ('cows', 'Cows / Cattle'),
        ('birds', 'Birds'),
        ('other', 'Other Animals'),
    )
    animals_helped = forms.MultipleChoiceField(
        choices=ANIMAL_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    about = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Tell us about your work...', 'rows': 4}),
        required=True
    )
    
    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter password',
            'id': 'id_password1'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password',
            'id': 'id_password2'
        })
    
    def save(self, commit=True):
        user = super().save(commit=False)
        # REMOVED: user.username = ... (Line 39 - your User model doesn't have username!)
        user.email = self.cleaned_data['email']
        user.user_type = 'individual'
        user.status = 'pending'
        
        if commit:
            user.save()
            
            # Create individual profile
            IndividualHelper.objects.create(
                user=user,
                full_name=self.cleaned_data['full_name'],
                mobile=self.cleaned_data['mobile'],
                location=self.cleaned_data['location'],
                whatsapp=self.cleaned_data.get('whatsapp', ''),
                instagram=self.cleaned_data.get('instagram', ''),
                animals_helped=', '.join(self.cleaned_data['animals_helped']),
                about=self.cleaned_data['about']
            )
        
        return user


class NGOForm(UserCreationForm):  # ← CHANGED: Line 59 (was NGORegistrationForm)
    """
    Registration form for NGOs
    """
    ngo_name = forms.CharField(
        max_length=200, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Animal Welfare NGO'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ngo@example.com'})
    )
    emergency_contact = forms.CharField(
        max_length=15, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 98765 43210'})
    )
    location = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Full address with landmarks', 'rows': 3}),
        required=True
    )
    whatsapp = forms.CharField(
        max_length=15, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 98765 43210'})
    )
    instagram = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '@ngo_handle'})
    )
    telegram = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '@ngo_telegram'})
    )
    
    SERVICE_CHOICES = (
        ('dogs', 'Dog Rescue & Care'),
        ('cats', 'Cat Rescue & Care'),
        ('cows', 'Cow / Cattle Care'),
        ('birds', 'Bird Rescue & Care'),
        ('medical', 'Medical Treatment'),
        ('shelter', 'Animal Shelter'),
        ('adoption', 'Adoption Services'),
    )
    services_provided = forms.MultipleChoiceField(
        choices=SERVICE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    operating_hours = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '9 AM - 6 PM or 24/7'})
    )
    certificate = forms.FileField(
        required=True,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'})
    )
    
    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter password',
            'id': 'ngo_id_password1'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password',
            'id': 'ngo_id_password2'
        })
    
    def save(self, commit=True):
        user = super().save(commit=False)
        # REMOVED: user.username = ... (Line 88 - your User model doesn't have username!)
        user.email = self.cleaned_data['email']
        user.user_type = 'ngo'
        user.status = 'pending'
        
        if commit:
            user.save()
            
            # Create NGO profile
            NGO.objects.create(
                user=user,
                ngo_name=self.cleaned_data['ngo_name'],
                email=self.cleaned_data['email'],
                emergency_contact=self.cleaned_data['emergency_contact'],
                location=self.cleaned_data['location'],
                whatsapp=self.cleaned_data.get('whatsapp', ''),
                instagram=self.cleaned_data.get('instagram', ''),
                telegram=self.cleaned_data.get('telegram', ''),
                services_provided=', '.join(self.cleaned_data['services_provided']),
                operating_hours=self.cleaned_data.get('operating_hours', ''),
                certificate=self.cleaned_data['certificate']
            )
        
        return user
