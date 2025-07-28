import datetime
import uuid
from typing import ClassVar
from typing_extensions import override
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES: list[tuple[str, str]] = [
        ('admin', 'Administrator'),
        ('user', 'Standard User'),
        ('viewer', 'Read-Only User'),
    ]
    username: str= models.CharField(max_length=150, unique=True)
    email: str= models.EmailField(unique=True)
    first_name: str= models.CharField(max_length=150, blank=True)
    last_name:str = models.CharField(max_length=150, blank=True)
    phone: str= models.CharField(max_length=150, blank=True)
    organization : str = models.CharField(max_length=150, blank=True)
    role: str= models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='user'
    )
    is_active: bool= models.BooleanField(default=True)
    last_login: datetime.datetime | None= models.DateTimeField(null=True, blank=True)
    created_at: datetime.datetime= models.DateTimeField(default=timezone.now)
    updated_at: datetime.datetime= models.DateTimeField(auto_now=True)
    id: uuid.UUID= models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    access_key_id: str= models.CharField(max_length=255, blank=True)
    secret_access_key: str= models.CharField(max_length=255, blank=True)

    USERNAME_FIELD: str = 'email'
    REQUIRED_FIELDS: list[str] = [ 'username', 'first_name', 'last_name']
    
    class Meta:
        db_table: str = 'accounts_user'
        ordering: list[str] = ['-created_at']
        
    @override
    def __str__(self) -> str:
        return f"{self.email} ({self.get_full_name() or self.username})"

    @override
    def get_full_name(self)-> str:
        return f"{self.first_name} {self.last_name}".strip()
    
    @override
    def get_short_name(self):
        return self.first_name or self.username
    
