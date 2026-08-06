from django.db import models
from django.conf import settings
from .product import Product

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="orders")

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    email_linked = models.EmailField(null=True)
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


    STATUS_CHOICE = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("packed", "Packed"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]
    
    status = models.CharField(max_length=20,choices=STATUS_CHOICE,default="pending")

    PAYMENT_STATUS = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default="pending")


    def __str__(self):
        return self.first_name


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")

    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name="order_items")

    product_name_snapshot = models.CharField(max_length=50)

    quantity = models.PositiveIntegerField()

    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    line_total = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["order", "product"]),
        ]

    def __str__(self):
        return f"{self.product_name_snapshot} x {self.quantity}"


class OrderUpdate(models.Model):
    update_id = models.AutoField(primary_key=True)

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="updates", null=True, blank=True)

    update_desc = models.CharField(max_length=5000)

    timestamp = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.update_desc[0:10] + '...'