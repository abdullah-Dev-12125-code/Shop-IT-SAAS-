from django.db import models

#Create your model here

class Product(models.Model):
    Product_name = models.CharField(max_length=50)
    category = models.CharField(max_length=50, default="")
    sub_category = models.CharField(max_length=50, default="")
    price = models.IntegerField(default=0)
    desc = models.CharField(max_length=300, default="")
    pub_date = models.DateField()
    image_url = models.URLField(blank=True, default="")
    image = models.ImageField(upload_to="shop/images", default="")

    @property
    def has_image_file(self):
        return bool(self.image and self.image.name and self.image.storage.exists(self.image.name))

    def __str__(self):
        return self.Product_name
    
class Contact(models.Model):
    msg_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50, default="")
    phone_number = models.IntegerField(max_length=50, default="")
    desc = models.CharField(max_length = 400, default="")

    def __str__(self):
        return self.name