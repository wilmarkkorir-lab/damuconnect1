from django.contrib.auth.models import AbstractUser
from django.db import models

ROLE_CHOICES = (
    ('admin', 'Admin'),
    ('entity', 'Entity'),
    ('donor', 'Donor'),
)

class User(AbstractUser):
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(unique=True)  # enforce unique email

    def __str__(self):
        return f"{self.username} ({self.role})"
