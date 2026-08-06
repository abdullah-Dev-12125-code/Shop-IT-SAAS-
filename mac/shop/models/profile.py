from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User



class Profile(models.Model):
    """
    Extended user profile model to store additional user information
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Profile information
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, help_text='User profile picture')
    banner = models.ImageField(upload_to='banners/', blank=True, null=True, help_text='User banner picture')
    
    bio = models.TextField(max_length=500, blank=True, default='', help_text='User biography or about section')
    
    # Contact information
    phone = models.CharField(max_length=20, blank=True,default='', help_text='User phone number')

    address = models.CharField(max_length=255, blank=True, default='', help_text='User address for shipping')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}'s Profile"
    
    def get_full_name(self):
        """Return user's full name"""
        return self.user.get_full_name() or self.user.username
    
    def get_short_name(self):
        """Return user's first name"""
        return self.user.first_name or self.user.username


# Signal to automatically create profile when user is created

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create a Profile instance when a new User is created
    """
    if created:
        Profile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save the Profile instance when User is saved
    """
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)

