from django.db import models



# Create your models here.
class ec2Instance(models.Model):
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

