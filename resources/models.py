from typing_extensions import override
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from accounts.models import User

# Create your models here.
class EC2Instance(models.Model):
    STATUS_CHOICES: tuple[tuple[str, str], ...] = (
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('stopped', 'Stopped'),
        ('terminated', 'Terminated'),
    )
    name: models.CharField = models.CharField(max_length=255, unique=True)
    ip_address: models.GenericIPAddressField = models.GenericIPAddressField(null=True, blank=True)
    port: models.PositiveIntegerField = models.PositiveIntegerField(
        default=22,
        validators=[MinValueValidator(1), MaxValueValidator(65535)]
    )
    creating_user: models.ForeignKey = models.ForeignKey(
        User,
        on_delete= models.DO_NOTHING,
        related_name='creating_user',
    )
    username: models.CharField = models.CharField(max_length=100)
    password: models.CharField = models.CharField(max_length=255, blank=True)
    ssh_key: models.TextField = models.TextField(blank=True, help_text="SSH private key for authentication")
    status: models.CharField = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at: models.DateTimeField = models.DateTimeField(default=timezone.now)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering: list[str] = ['-created_at']
    
    @override
    def __str__(self):
        return f"{self.name} ({self.status})"
    
    def create_instance(self):
        pass
        
    def terminate_instance(self):
        pass    
        
    def get_instance_status(self):
        pass    
        
    def get_instance_ip_address(self):
        pass    
        
    def get_instance_port(self):
        pass

        




