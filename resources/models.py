from typing_extensions import override
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from resources.api.api_resources import create_ec2_instance
from accounts.models import User
from resources.api.api_resources import get_ec2_client

# Create your models here.
# pyright: reportInvalidTypeArguments=false
class EC2Instance(models.Model):
    id: int
    
    INSTANCE_TYPE_CHOICES: tuple[tuple[str, str], ...] = (
        ('t2.nano', 't2.nano'),
        ('t2.micro', 't2.micro'),
        ('t2.small', 't2.small'),
        ('t2.medium', 't2.medium'),
        ('t2.large', 't2.large'),
        ('t3.nano', 't3.nano'),
        ('t3.micro', 't3.micro'),
        ('t3.small', 't3.small'),
        ('t3.medium', 't3.medium'),
        ('t3.large', 't3.large'),
    )
    # this is the AMI ID for the Ubuntu 20.04 LTS AMI in us-east-1
    AMI_ID: str = "ami-08a6efd148b1f7504"
    STATUS_CHOICES: tuple[tuple[str, str], ...] = (
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('stopped', 'Stopped'),
        ('terminated', 'Terminated'),
    )
    REGION_CHOICES: tuple[tuple[str, str], ...] = (
        ('us-east-1', 'US East (N. Virginia)'),
        ('us-east-2', 'US East (Ohio)'),
        ('us-west-1', 'US West (N. California)'),
        ('us-west-2', 'US West (Oregon)'),
        ('ca-central-1', 'Canada (Central)'),
        ('eu-central-1', 'Europe (Frankfurt)'),
        ('eu-west-1', 'Europe (Ireland)'),
        ('eu-west-2', 'Europe (London)'),
        ('eu-west-3', 'Europe (Paris)'),
        ('eu-north-1', 'Europe (Stockholm)'),
        ('ap-northeast-1', 'Asia Pacific (Tokyo)'),
        ('ap-northeast-2', 'Asia Pacific (Seoul)'),
        ('ap-southeast-1', 'Asia Pacific (Singapore)'),
        ('ap-southeast-2', 'Asia Pacific (Sydney)'),
        ('ap-south-1', 'Asia Pacific (Mumbai)'),
        ('sa-east-1', 'South America (São Paulo)'),
    )

    name: str= models.CharField(max_length=255, unique=True) 
    ip_address: str= models.GenericIPAddressField(null=True, blank=True)  
    port: str= models.PositiveIntegerField(
        default=22,
        validators=[MinValueValidator(1), MaxValueValidator(65535)]
    )
    creating_user: User= models.ForeignKey(
        User,
        on_delete= models.DO_NOTHING,
        related_name='creating_user',
    )
    username: str= models.CharField(max_length=100)
    password: str= models.CharField(max_length=255, blank=True)
    ssh_key: str= models.TextField(blank=True, help_text="SSH private key for authentication")
    instance_type: str= models.CharField(
        max_length=20,
        choices=INSTANCE_TYPE_CHOICES,
        default='t2.micro'
    )
    aws_instance_id: str= models.CharField(
        max_length=20, 
        blank=True, 
        null=True, 
        help_text="AWS EC2 instance ID (e.g., i-1234567890abcdef0)",
        unique=True
    )
    region: str= models.CharField(max_length=20, choices=REGION_CHOICES, default='us-east-1')
    status: str= models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at: str= models.DateTimeField(default=timezone.now)
    updated_at: str= models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering: list[str] = ['-created_at']
    
    @override
    def __str__(self):
        return f"{self.name} ({self.status})"
    
    def create_instance(self) -> str | None:
        
        instance_id = create_ec2_instance(
            user=self.creating_user,
            ami_id=self.AMI_ID,
            instance_type=self.instance_type
        )
        
        if instance_id:
            self.aws_instance_id = instance_id
            self.status = 'pending'
            self.save()
            return instance_id
        return None
    def start_instance(self) -> bool:
        from resources.api.api_resources import start_ec2_instances
        
        if not self.aws_instance_id:
            return False
            
        response = start_ec2_instances(
            user=self.creating_user,
            instance_ids=[self.aws_instance_id]
        )
        
        if response:
            self.status = 'running'
            self.save()
            return True
        return False
        
    def stop_instance(self):
        from resources.api.api_resources import stop_ec2_instances
        
        if not self.aws_instance_id:
            return False
            
        response = stop_ec2_instances(
            user=self.creating_user,
            instance_ids=[self.aws_instance_id]
        )
        
        if response:
            self.status = 'stopped'
            self.save()
            return True
        return False    

    def terminate_instance(self) -> bool:
        from resources.api.api_resources import terminate_ec2_instances
        
        if not self.aws_instance_id:
            return False
            
        response = terminate_ec2_instances(
            user=self.creating_user,
            instance_ids=[self.aws_instance_id]
        )
        
        if response:
            self.status = 'terminated'
            self.save()
            return True
        return False    
        
    def get_instance_status(self)-> str | None:
        
        if not self.aws_instance_id:
            return None
            
        try:
            ec2 = get_ec2_client(self.creating_user)
            response = ec2.describe_instances(InstanceIds=[self.aws_instance_id])
            
            if response['Reservations']:
                instance = response['Reservations'][0]['Instances'][0]
                status = instance['State']['Name']
                
                if status != self.status:
                    self.status = status
                    self.save()
                    
                return status
        except Exception as e:
            print(f"Error getting instance status: {e}")
        return None    
        
    def get_instance_ip_address(self):
        
        if not self.aws_instance_id:
            return None
            
        try:
            ec2 = get_ec2_client(self.creating_user)
            response = ec2.describe_instances(InstanceIds=[self.aws_instance_id])
            
            if response['Reservations']:
                instance = response['Reservations'][0]['Instances'][0]
                public_ip = instance.get('PublicIpAddress')
                
                if public_ip and public_ip != self.ip_address:
                    self.ip_address = public_ip
                    self.save()
                    
                return public_ip
        except Exception as e:
            print(f"Error getting instance IP: {e}")
        return None    
        

        




