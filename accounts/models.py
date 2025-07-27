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
    username: models.CharField = models.CharField(max_length=150, unique=True)
    email: models.EmailField = models.EmailField(unique=True)
    first_name: models.CharField = models.CharField(max_length=150, blank=True)
    last_name: models.CharField = models.CharField(max_length=150, blank=True)
    phone: models.CharField = models.CharField(max_length=150, blank=True)
    organization: models.CharField = models.CharField(max_length=150, blank=True)
    role: models.CharField = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='user'
    )
    is_active: models.BooleanField = models.BooleanField(default=True)
    last_login: models.DateTimeField = models.DateTimeField(null=True, blank=True)
    created_at: models.DateTimeField = models.DateTimeField(default=timezone.now)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)
    id: models.UUIDField = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    USERNAME_FIELD: str = 'email'
    REQUIRED_FIELDS: ClassVar[list[str]] = [ 'username', 'first_name', 'last_name']
    
    class Meta:
        db_table: str = 'accounts_user'
        ordering: list[str] = ['-created_at']
        
    @override
    def __str__(self) -> str:
        return f"{self.email} ({self.get_full_name() or self.username})"

    @override
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    @override
    def get_short_name(self):
        return self.first_name or self.username
    
