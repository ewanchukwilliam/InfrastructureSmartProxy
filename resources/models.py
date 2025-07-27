import datetime
from typing_extensions import override
import uuid
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from accounts.models import User



# Create your models here.
class ec2Instance(models.Model):
    STATUS_CHOICES: tuple[tuple[str, str], ...] = (
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('stopped', 'Stopped'),
        ('terminated', 'Terminated'),
    )
    name: models.CharField[str, str] = models.CharField(max_length=255, unique=True)
    ip_address: models.GenericIPAddressField[str, int] = models.GenericIPAddressField(null=True, blank=True)
    port: models.PositiveIntegerField[int, int] = models.PositiveIntegerField(
        default=22,
        validators=[MinValueValidator(1), MaxValueValidator(65535)]
    )
    creating_user: models.ForeignKey[User, uuid.UUID] = models.ForeignKey(
        'Users',
        on_delete= models.DO_NOTHING,
        related_name='creating_user',
    )
    username: models.CharField[str, str] = models.CharField(max_length=100)
    password: models.CharField[str, str] = models.CharField(max_length=255, blank=True)
    ssh_key: models.TextField[str, str] = models.TextField(blank=True, help_text="SSH private key for authentication")
    status: models.CharField[str, str] = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at: models.DateTimeField[datetime.datetime, datetime.datetime] = models.DateTimeField(default=timezone.now)
    updated_at: models.DateTimeField[datetime.datetime, datetime.datetime] = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table: str = 'accounts_container'
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

        




