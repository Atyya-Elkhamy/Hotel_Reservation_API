from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


# Create your models here.

class User(AbstractUser):
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('hotel_staff','Hotel Staff'),
        ('hotel_owner', 'Hotel Owner'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(blank=True, null=True, unique=True)
    email = models.EmailField(unique=True)
    confirmed = models.BooleanField(default=False)

    def is_confirmed(self):
        return self.confirmed

    def set_confirmed(self):
        self.confirmed = True
        self.save()

    def __str__(self):
        return self.username
    class Meta():
        db_table ="accounts"
