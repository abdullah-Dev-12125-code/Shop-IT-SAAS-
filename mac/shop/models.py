from django.db import models
from django.utils import timezone

#Create your model here




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
    available_now = models.IntegerField(max_length=20, blank=False, null=False)


    @property
    def has_image_file(self):
        return bool(self.image and self.image.name and self.image.storage.exists(self.image.name))


    def __str__(self):
        return self.product_name
    



class Contact(models.Model):
    msg_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50, default="")
    phone_number = models.IntegerField(max_length=50, default="")
    desc = models.CharField(max_length = 400, default="")


    def __str__(self):
        return self.name
    



class Order(models.Model):
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