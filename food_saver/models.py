from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = (
        ('donor', 'Food Donor'),
        ('ngo', 'NGO'),
        ('volunteer', 'Volunteer'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='donor')
    phone = models.CharField(max_length=20, blank=True)
    location_lat = models.FloatField(null=True, blank=True)
    location_lng = models.FloatField(null=True, blank=True)
    reward_points = models.IntegerField(default=0)
    is_fraudulent = models.BooleanField(default=False)
    address = models.TextField(blank=True)

class FoodDonation(models.Model):
    FOOD_TYPE_CHOICES = (
        ('veg', 'Vegetarian'),
        ('non-veg', 'Non-Vegetarian'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('picked_up', 'Picked Up'),
        ('delivered', 'Delivered'),
    )
    donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donations')
    name = models.CharField(max_length=200)
    food_type = models.CharField(max_length=50, choices=FOOD_TYPE_CHOICES) # Changed max_length from 10 to 50
    quantity = models.CharField(max_length=100) # e.g., "5 kg", "10 servings"
    image = models.ImageField(upload_to='food_images/', null=True, blank=True)
    preparation_time = models.DateTimeField()
    expiry_time = models.DateTimeField(null=True, blank=True)
    address = models.TextField(blank=True)
    location_lat = models.FloatField()
    location_lng = models.FloatField()
    special_instructions = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.expiry_time

class Pickup(models.Model):
    donation = models.OneToOneField(FoodDonation, on_delete=models.CASCADE, related_name='pickup')
    ngo = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ngo_pickups')
    volunteer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='volunteer_tasks')
    accepted_at = models.DateTimeField(auto_now_add=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
