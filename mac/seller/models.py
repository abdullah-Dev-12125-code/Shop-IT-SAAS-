from django.conf import settings
from django.db import models

# Create your models here.

class Seller(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="seller_profile")

    store_name = models.CharField(max_length=150, unique=True)
    parent_organization = models.CharField(max_length=150, blank=True)

    phone = models.CharField(max_length=20)
    email_linked = models.EmailField()
    email_vendor = models.EmailField()

    address = models.TextField(max_length=150)

    profile_image = models.ImageField(upload_to='profile_images/',  null=True, blank=True)
    store_banner = models.ImageField(upload_to='store_banners/', null=True, blank=True)

    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.store_name
    