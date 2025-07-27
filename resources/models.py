from typing_extensions import override
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from accounts.models import User
from resources.api.api_resources import get_ec2_client

# Create your models here.
# pyright: reportInvalidTypeArguments=false
class EC2Instance(models.Model):
    INSTANCE_TYPE: str = "t2.micro"
    # this is the AMI ID for the Ubuntu 20.04 LTS AMI in us-east-1
    AMI_ID: str = "ami-08a6efd148b1f7504"
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
    instance_type: models.CharField = models.CharField(
        max_length=20,
        choices=INSTANCE_TYPE,
        default='t2.micro'
    )
    region: models.CharField = models.CharField(max_length=20, default='us-east-1')
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
    
    def create_instance(self, User: User):
        client = get_ec2_client(User)


        
        
    def start_instance(self):
        pass
        
    def stop_instance(self):
        pass    

    def terminate_instance(self):
        pass    
        
    def get_instance_status(self):
        pass    
        
    def get_instance_ip_address(self):
        pass    
        

        




