"""
User and Profile Models for Animal Mitra
Created by: Dev Panchal

AI Assistance: ChatGPT helped me understand Django's AbstractBaseUser,
model relationships, and signals. All code was reviewed and customized
for Animal Mitra's specific requirements.
"""


"""
Database models for users, individual helpers, and NGOs
"""
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class CustomUserManager(BaseUserManager):
    """
    Custom user manager for email-based authentication
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email address is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'admin')
        extra_fields.setdefault('status', 'verified')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom user model extending Django's default User
    """
    USER_TYPE_CHOICES = (
        ('individual', 'Individual Helper'),
        ('ngo', 'NGO'),
        ('admin', 'Admin'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('pending_update', 'Pending Update Approval'),
        ('deletion_requested', 'Deletion Requested'),
    )
    
    # Remove username, use email instead
    username = None
    email = models.EmailField(unique=True)
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Set email as the login field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    # Use custom manager
    objects = CustomUserManager()
    
    def __str__(self):
        return f"{self.email} ({self.user_type})"
    
    class Meta:
        ordering = ['-created_at']


class IndividualHelper(models.Model):
    """
    Profile for individual animal helpers
    """
    ANIMAL_CHOICES = (
        ('dogs', 'Dogs'),
        ('cats', 'Cats'),
        ('cows', 'Cows / Cattle'),
        ('birds', 'Birds'),
        ('other', 'Other Animals'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='individual_profile')
    full_name = models.CharField(max_length=200)
    mobile = models.CharField(max_length=15)
    location = models.CharField(max_length=200)
    whatsapp = models.CharField(max_length=15, blank=True)
    instagram = models.CharField(max_length=100, blank=True)
    animals_helped = models.CharField(max_length=200)  # Comma-separated
    about = models.TextField()
    
    # Statistics
    profile_views = models.IntegerField(default=0)
    calls_received = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.full_name
    
    def get_animals_list(self):
        """Return animals as a list"""
        return [animal.strip() for animal in self.animals_helped.split(',')]
    
    class Meta:
        ordering = ['-created_at']


class NGO(models.Model):
    """
    Profile for NGO organizations
    """
    SERVICE_CHOICES = (
        ('dogs', 'Dog Rescue & Care'),
        ('cats', 'Cat Rescue & Care'),
        ('cows', 'Cow / Cattle Care'),
        ('birds', 'Bird Rescue & Care'),
        ('medical', 'Medical Treatment'),
        ('shelter', 'Animal Shelter'),
        ('adoption', 'Adoption Services'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ngo_profile')
    ngo_name = models.CharField(max_length=200)
    email = models.EmailField()
    emergency_contact = models.CharField(max_length=15)
    location = models.TextField()
    whatsapp = models.CharField(max_length=15, blank=True)
    instagram = models.CharField(max_length=100, blank=True)
    telegram = models.CharField(max_length=100, blank=True)
    services_provided = models.CharField(max_length=300)  # Comma-separated
    operating_hours = models.CharField(max_length=100, blank=True)
    certificate = models.FileField(upload_to='certificates/', blank=True)
    
    # Statistics
    profile_views = models.IntegerField(default=0)
    emergency_calls = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.ngo_name
    
    def get_services_list(self):
        """Return services as a list"""
        return [service.strip() for service in self.services_provided.split(',')]
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'NGO'
        verbose_name_plural = 'NGOs'


class PendingProfileUpdate(models.Model):
    """
    Store pending profile changes awaiting admin approval
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pending_update')
    data = models.JSONField()  # Store all changed fields as JSON
    requested_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Pending update for {self.user.email}"
    
    class Meta:
        ordering = ['-requested_at']
