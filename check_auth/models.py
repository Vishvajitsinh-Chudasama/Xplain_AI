from django.db import models
from django.utils import timezone
from datetime import timedelta

class UserInfo(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    password = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

class OTP(models.Model):
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        """
        Checks if the OTP is still valid (e.g., within 5 minutes).
        """
        return self.created_at >= timezone.now() - timedelta(minutes=5)

    def __str__(self):
        return f"OTP for {self.email}"