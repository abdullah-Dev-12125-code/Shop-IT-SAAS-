from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

#Create your model here

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






class Product(models.Model):
    product_name = models.CharField(max_length=50)
    category = models.CharField(max_length=50, default="")
    sub_category = models.CharField(max_length=50, default="")
    price = models.IntegerField(default=0)
    desc = models.CharField(max_length=300, default="")
    pub_date = models.DateField(default=timezone.now)
    image_url = models.URLField(blank=True, default="")
    image = models.ImageField(upload_to="shop/images", default="")
    stock_status = models.CharField(max_length=20, default="In Stock")
    available_now = models.IntegerField(blank=False, null=False)


    @property
    def has_image_file(self):
        return bool(self.image and self.image.name and self.image.storage.exists(self.image.name))


    def __str__(self):
        return self.product_name
    



class Contact(models.Model):
    msg_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50, default="")
    phone_number = models.IntegerField(default="")
    desc = models.CharField(max_length = 400, default="")


    def __str__(self):
        return self.name
    



class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    email_linked = models.EmailField(null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=50)
    payment_method = models.CharField(max_length=20)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    item_json = models.TextField(default="{}")
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.first_name
    



class OrderUpdate(models.Model):
    update_id = models.AutoField(primary_key=True)
    order_id = models.IntegerField(default="")
    update_desc = models.CharField(max_length=5000)
    timestamp = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.update_desc[0:10] + '...'