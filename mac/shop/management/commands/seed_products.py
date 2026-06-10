import os
import tempfile
import urllib.request
import uuid

from datetime import date

from django.core.files import File
from django.core.management.base import BaseCommand

from shop.models import Product


# --- Unsplash direct image URLs — each carefully matched to the product context ---
# These are permanent, hotlink-safe Unsplash URLs that actually show the product.
PRODUCTS = [
    {
        "name": "Aurora Noise-Canceling Headphones",
        "category": "Audio",
        "sub_category": "Headphones",
        "price": 179,
        "desc": "Wireless over-ear headphones with active noise cancellation, deep bass, and all-day comfort for travel or focused work.",
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&h=400&fit=crop",
    },
    {
        "name": "PulseFit Smart Watch",
        "category": "Wearables",
        "sub_category": "Smart Watch",
        "price": 149,
        "desc": "A sleek fitness watch that tracks heart rate, steps, sleep, and workouts while keeping notifications on your wrist.",
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&h=400&fit=crop",
    },
    {
        "name": "Nova Mechanical Keyboard",
        "category": "Computing",
        "sub_category": "Keyboard",
        "price": 129,
        "desc": "A compact mechanical keyboard with tactile switches, RGB lighting, and a solid aluminum frame for fast typing.",
        "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&h=400&fit=crop",
    },
    {
        "name": "Orbit Gaming Mouse",
        "category": "Gaming",
        "sub_category": "Mouse",
        "price": 89,
        "desc": "An ergonomic gaming mouse with a precision sensor, programmable buttons, and a lightweight shell for quick aim.",
        "image_url": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=600&h=400&fit=crop",
    },
    {
        "name": "Lumen Desk Lamp",
        "category": "Home Office",
        "sub_category": "Lighting",
        "price": 59,
        "desc": "A modern desk lamp with adjustable brightness, warm and cool modes, and a slim design for clean workspaces.",
        "image_url": "https://images.unsplash.com/photo-1534105615256-13940a56ff44?w=600&h=400&fit=crop",
    },
    {
        "name": "TrailCam Action Camera",
        "category": "Cameras",
        "sub_category": "Action Camera",
        "price": 219,
        "desc": "Rugged 4K action camera built for biking, hiking, and travel with stabilization and water resistance.",
        "image_url": "https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=600&h=400&fit=crop",
    },
    {
        "name": "PureAir Smart Purifier",
        "category": "Home",
        "sub_category": "Air Purifier",
        "price": 249,
        "desc": "A quiet smart air purifier that filters dust, pollen, and odors while showing live air quality on the display.",
        "image_url": "https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=600&h=400&fit=crop",
    },
    {
        "name": "Glide Pro Wireless Earbuds",
        "category": "Audio",
        "sub_category": "Earbuds",
        "price": 99,
        "desc": "Pocket-friendly wireless earbuds with a charging case, low-latency mode, and clear call quality.",
        "image_url": "https://images.unsplash.com/photo-1572569511254-d8f925fe2cbb?w=600&h=400&fit=crop",
    },
    {
        "name": "Metro USB-C Hub",
        "category": "Accessories",
        "sub_category": "Hub",
        "price": 69,
        "desc": "A versatile USB-C hub with HDMI, USB-A, SD card, and charging passthrough for modern laptops.",
        "image_url": "https://images.unsplash.com/photo-1625723044792-44de16ccb4e9?w=600&h=400&fit=crop",
    },
    {
        "name": "CrystalBook Laptop Stand",
        "category": "Accessories",
        "sub_category": "Stand",
        "price": 45,
        "desc": "An adjustable aluminum laptop stand that raises your screen, improves airflow, and cleans up the desk.",
        "image_url": "https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=600&h=400&fit=crop",
    },
    {
        "name": "Vertex 27\" 4K Monitor",
        "category": "Computing",
        "sub_category": "Monitor",
        "price": 349,
        "desc": "A stunning 27-inch 4K IPS monitor with HDR10, thin bezels, and USB-C connectivity for creative professionals.",
        "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=600&h=400&fit=crop",
    },
    {
        "name": "Bolt 65W GaN Charger",
        "category": "Accessories",
        "sub_category": "Charger",
        "price": 39,
        "desc": "Ultra-compact 65W GaN fast charger with dual USB-C ports — charge your laptop and phone simultaneously.",
        "image_url": "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=600&h=400&fit=crop",
    },
    {
        "name": "SonicBar Bluetooth Speaker",
        "category": "Audio",
        "sub_category": "Speaker",
        "price": 79,
        "desc": "Portable Bluetooth speaker with 360° sound, IPX7 waterproof rating, and 20-hour battery life for outdoor adventures.",
        "image_url": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=600&h=400&fit=crop",
    },
    {
        "name": "ErgoFlex Office Chair",
        "category": "Home Office",
        "sub_category": "Chair",
        "price": 299,
        "desc": "Ergonomic mesh office chair with adjustable lumbar support, headrest, and breathable fabric for all-day comfort.",
        "image_url": "https://images.unsplash.com/photo-1592078615290-033ee584e267?w=600&h=400&fit=crop",
    },
    {
        "name": "SnapLens Mirrorless Camera",
        "category": "Cameras",
        "sub_category": "Mirrorless",
        "price": 599,
        "desc": "Compact mirrorless camera with a 24MP sensor, 4K video, and fast autofocus — perfect for vlogging and street photography.",
        "image_url": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=600&h=400&fit=crop",
    },
    {
        "name": "FlexDesk Standing Desk",
        "category": "Home Office",
        "sub_category": "Desk",
        "price": 449,
        "desc": "Electric height-adjustable standing desk with memory presets, cable management tray, and a spacious bamboo top.",
        "image_url": "https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?w=600&h=400&fit=crop",
    },
]


class Command(BaseCommand):
    help = (
        "Clear all products and seed 10 new products with properly matched "
        "picsum.photos URLs AND downloaded local image files."
    )

    def handle(self, *args, **options):
        Product.objects.all().delete()
        created = []
        errors = []

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

            # ---- download image to populate the ImageField ----
            try:
                self._download_image(product, item["image_url"])
            except Exception as exc:
                errors.append(f"{item['name']}: {exc}")

            created.append(product)

        if errors:
            self.stdout.write(self.style.WARNING(f"Seeded {len(created)} products, {len(errors)} image-download failures:"))
            for e in errors:
                self.stdout.write(self.style.WARNING(f"  • {e}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Seeded {len(created)} products with local images."))

    # ------------------------------------------------------------------
    def _download_image(self, product, url):
        """Fetch *url* and attach it to *product.image* as a local file."""
        ext = ".jpg"
        filename = f"{uuid.uuid4().hex}{ext}"
        tmp_path = os.path.join(tempfile.gettempdir(), filename)

        self.stdout.write(f"  Downloading {url}  ->  {filename} …")
        urllib.request.urlretrieve(url, tmp_path)

        with open(tmp_path, "rb") as f:
            product.image.save(filename, File(f), save=True)

        os.remove(tmp_path)
