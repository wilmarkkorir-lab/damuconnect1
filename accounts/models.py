from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import random

ROLE_CHOICES = (
    ('admin', 'Admin'),
    ('entity', 'Entity'),
    ('donor', 'Donor'),
)

class User(AbstractUser):
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.username} ({self.role})"


class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        # OTP expires after 10 minutes
        return timezone.now() > self.created_at + timezone.timedelta(minutes=10)

    @classmethod
    def generate_for(cls, user):
        # Invalidate any existing OTPs for this user
        cls.objects.filter(user=user, is_used=False).delete()
        otp = str(random.randint(100000, 999999))
        return cls.objects.create(user=user, otp=otp)

    def __str__(self):
        return f"{self.user.email} — {self.otp}"
