from datetime import date

from django.core.management.base import BaseCommand

from shop.models import Product


PRODUCTS = [
    {
        "name": "Aurora Noise-Canceling Headphones",
        "category": "Audio",
        "sub_category": "Headphones",
        "price": 179,
        "desc": "Wireless over-ear headphones with active noise cancellation, deep bass, and all-day comfort for travel or focused work.",
        "image_url": "https://source.unsplash.com/featured/1200x900/?headphones",
    },
    {
        "name": "PulseFit Smart Watch",
        "category": "Wearables",
        "sub_category": "Smart Watch",
        "price": 149,
        "desc": "A sleek fitness watch that tracks heart rate, steps, sleep, and workouts while keeping notifications on your wrist.",
        "image_url": "https://source.unsplash.com/featured/1200x900/?smartwatch,fitness",
    },
    {
        "name": "Nova Mechanical Keyboard",
        "category": "Computing",
        "sub_category": "Keyboard",
        "price": 129,
        "desc": "A compact mechanical keyboard with tactile switches, RGB lighting, and a solid aluminum frame for fast typing.",
        "image_url": "https://source.unsplash.com/featured/1200x900/?mechanical-keyboard,gaming",
    },
    {
        "name": "Orbit Gaming Mouse",
        "category": "Gaming",
        "sub_category": "Mouse",
        "price": 89,
        "desc": "An ergonomic gaming mouse with a precision sensor, programmable buttons, and a lightweight shell for quick aim.",
        "image_url": "https://source.unsplash.com/featured/1200x900/?gaming-mouse",
    },
    {
        "name": "Lumen Desk Lamp",
        "category": "Home Office",
        "sub_category": "Lighting",
        "price": 59,
        "desc": "A modern desk lamp with adjustable brightness, warm and cool modes, and a slim design for clean workspaces.",
        "image_url": "https://source.unsplash.com/featured/1200x900/?desk-lamp,workspace",
    },
    {
        "name": "TrailCam Action Camera",
        "category": "Cameras",
        "sub_category": "Action Camera",
        "price": 219,
        "desc": "Rugged 4K action camera built for biking, hiking, and travel with stabilization and water resistance.",
        "image_url": "https://source.unsplash.com/featured/1200x900/?action-camera,travel",
    },
    {
        "name": "PureAir Smart Purifier",
        "category": "Home",
        "sub_category": "Air Purifier",
        "price": 249,
        "desc": "A quiet smart air purifier that filters dust, pollen, and odors while showing live air quality on the display.",
        "image_url": "https://source.unsplash.com/featured/1200x900/?air-purifier,home",
    },
    {
        "name": "Glide Pro Wireless Earbuds",
        "category": "Audio",
        "sub_category": "Earbuds",
        "price": 99,
        "desc": "Pocket-friendly wireless earbuds with a charging case, low-latency mode, and clear call quality.",
        "image_url": "https://source.unsplash.com/featured/1200x900/?wireless-earbuds,audio",
    },
    {
        "name": "Metro USB-C Hub",
        "category": "Accessories",
        "sub_category": "Hub",
        "price": 69,
        "desc": "A versatile USB-C hub with HDMI, USB-A, SD card, and charging passthrough for modern laptops.",
        "image_url": "https://source.unsplash.com/featured/1200x900/?usb-c-hub,laptop-accessory",
    },
    {
        "name": "CrystalBook Laptop Stand",
        "category": "Accessories",
        "sub_category": "Stand",
        "price": 45,
        "desc": "An adjustable aluminum laptop stand that raises your screen, improves airflow, and cleans up the desk.",
        "image_url": "https://source.unsplash.com/featured/1200x900/?laptop-stand,desk",
    },
]


class Command(BaseCommand):
    help = "Clear all products and seed 10 new products with generated matching images."

    def handle(self, *args, **options):
        Product.objects.all().delete()

        created_products = []
        for item in PRODUCTS:
            product = Product.objects.create(
                Product_name=item["name"],
                category=item["category"],
                sub_category=item["sub_category"],
                price=item["price"],
                desc=item["desc"],
                pub_date=date.today(),
                image_url=item["image_url"],
            )
            created_products.append(product)

        self.stdout.write(self.style.SUCCESS(f"Deleted old products and created {len(created_products)} new products."))
