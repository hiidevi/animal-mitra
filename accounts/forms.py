"""
Forms for user registration (Individual and NGO)
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, IndividualHelper, NGO

class IndividualRegistrationForm(UserCreationForm):
    """
    Registration form for individual helpers
    """
    full_name = forms.CharField(max_length=200, required=True)
    email = forms.EmailField(required=True)
    mobile = forms.CharField(max_length=15, required=True)
    location = forms.CharField(max_length=200, required=True)
    whatsapp = forms.CharField(max_length=15, required=False)
    instagram = forms.CharField(max_length=100, required=False)
    
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
    about = forms.CharField(widget=forms.Textarea, required=True)
    
    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
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


class NGORegistrationForm(UserCreationForm):
    """
    Registration form for NGOs
    """
    ngo_name = forms.CharField(max_length=200, required=True)
    email = forms.EmailField(required=True)
    emergency_contact = forms.CharField(max_length=15, required=True)
    location = forms.CharField(widget=forms.Textarea, required=True)
    whatsapp = forms.CharField(max_length=15, required=False)
    instagram = forms.CharField(max_length=100, required=False)
    telegram = forms.CharField(max_length=100, required=False)
    
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
    operating_hours = forms.CharField(max_length=100, required=False)
    certificate = forms.FileField(required=True)
    
    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
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