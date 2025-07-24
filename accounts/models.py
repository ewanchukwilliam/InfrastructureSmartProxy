from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('user', 'Standard User'),
        ('viewer', 'Read-Only User'),
    ]
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    organization = models.CharField(max_length=255, blank=True)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='user'
    )
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        db_table = 'accounts_user'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.email} ({self.get_full_name() or self.username})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        return self.first_name or self.username
    
class Container(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('stopped', 'Stopped'),
        ('error', 'Error'),
        ('terminated', 'Terminated'),
    ]
    
    name = models.CharField(max_length=255, unique=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    port = models.PositiveIntegerField(
        default=22,
        validators=[MinValueValidator(1), MaxValueValidator(65535)]
    )
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=255, blank=True)
    ssh_key = models.TextField(blank=True, help_text="SSH private key for authentication")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'accounts_container'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.status})"
