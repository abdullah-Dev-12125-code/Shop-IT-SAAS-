from django.db import models
from django.utils import timezone


class Product(models.Model):
    seller = models.ForeignKey('seller.Seller', on_delete=models.SET_NULL, null=True, blank=True, related_name='products', db_index=True,)
    product_name = models.CharField(max_length=50)
    category = models.CharField(max_length=50, default="")
    sub_category = models.CharField(max_length=50, default="")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0   )
    desc = models.CharField(max_length=300, default="")
    pub_date = models.DateField(default=timezone.now)
    image_url = models.URLField(blank=True, default="")
    image = models.ImageField(upload_to="shop/images", default="")
    stock_status = models.CharField(max_length=20, default="In Stock")
    available_now = models.IntegerField(blank=False, null=False)

    class Meta:
        indexes = [
            models.Index(fields=['seller', 'category']),
            models.Index(fields=['seller', 'sub_category']),
        ]


    @property
    def has_image_file(self):
        return bool(self.image and self.image.name and self.image.storage.exists(self.image.name))


    def __str__(self):
        return self.product_name