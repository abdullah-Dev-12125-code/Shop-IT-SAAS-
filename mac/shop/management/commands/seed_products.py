import os
import shutil
import tempfile
import urllib.request
import uuid

from datetime import date

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from shop.models import Product


def _product(name, category, sub_category, price, desc, image_url, available_now):
    return {
        "name": name,
        "category": category,
        "sub_category": sub_category,
        "price": price,
        "desc": desc,
        "image_url": image_url,
        "available_now": available_now,
    }


PRODUCTS = [
    _product(
        "Aurora Noise-Canceling Headphones",
        "Audio",
        "Headphones",
        179,
        "Wireless over-ear headphones with active noise cancellation, deep bass, and all-day comfort for travel or focused work.",
        "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&h=400&fit=crop",
        18,
    ),
    _product(
        "PulseFit Smart Watch",
        "Wearables",
        "Smart Watch",
        149,
        "A sleek fitness watch that tracks heart rate, steps, sleep, and workouts while keeping notifications on your wrist.",
        "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&h=400&fit=crop",
        15,
    ),
    _product(
        "Nova Mechanical Keyboard",
        "Computing",
        "Keyboard",
        129,
        "A compact mechanical keyboard with tactile switches, RGB lighting, and a solid aluminum frame for fast typing.",
        "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&h=400&fit=crop",
        21,
    ),
    _product(
        "Orbit Gaming Mouse",
        "Gaming",
        "Mouse",
        89,
        "An ergonomic gaming mouse with a precision sensor, programmable buttons, and a lightweight shell for quick aim.",
        "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=600&h=400&fit=crop",
        24,
    ),
    _product(
        "Lumen Desk Lamp",
        "Home Office",
        "Lighting",
        59,
        "A modern desk lamp with adjustable brightness, warm and cool modes, and a slim design for clean workspaces.",
        "https://images.unsplash.com/photo-1534105615256-13940a56ff44?w=600&h=400&fit=crop",
        30,
    ),
    _product(
        "TrailCam Action Camera",
        "Cameras",
        "Action Camera",
        219,
        "Rugged 4K action camera built for biking, hiking, and travel with stabilization and water resistance.",
        "https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=600&h=400&fit=crop",
        9,
    ),
    _product(
        "PureAir Smart Purifier",
        "Home",
        "Air Purifier",
        249,
        "A quiet smart air purifier that filters dust, pollen, and odors while showing live air quality on the display.",
        "https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=600&h=400&fit=crop",
        12,
    ),
    _product(
        "Glide Pro Wireless Earbuds",
        "Audio",
        "Earbuds",
        99,
        "Pocket-friendly wireless earbuds with a charging case, low-latency mode, and clear call quality.",
        "https://images.unsplash.com/photo-1572569511254-d8f925fe2cbb?w=600&h=400&fit=crop",
        26,
    ),
    _product(
        "Metro USB-C Hub",
        "Accessories",
        "Hub",
        69,
        "A versatile USB-C hub with HDMI, USB-A, SD card, and charging passthrough for modern laptops.",
        "https://images.unsplash.com/photo-1625723044792-44de16ccb4e9?w=600&h=400&fit=crop",
        14,
    ),
    _product(
        "CrystalBook Laptop Stand",
        "Accessories",
        "Stand",
        45,
        "An adjustable aluminum laptop stand that raises your screen, improves airflow, and cleans up the desk.",
        "https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=600&h=400&fit=crop",
        17,
    ),
    _product(
        "Vertex 27-Inch 4K Monitor",
        "Computing",
        "Monitor",
        349,
        "A stunning 27-inch 4K IPS monitor with HDR10, thin bezels, and USB-C connectivity for creative professionals.",
        "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=600&h=400&fit=crop",
        8,
    ),
    _product(
        "Bolt 65W GaN Charger",
        "Accessories",
        "Charger",
        39,
        "Ultra-compact 65W GaN fast charger with dual USB-C ports that can charge a laptop and phone at the same time.",
        "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=600&h=400&fit=crop",
        32,
    ),
    _product(
        "SonicBar Bluetooth Speaker",
        "Audio",
        "Speaker",
        79,
        "Portable Bluetooth speaker with 360-degree sound, IPX7 waterproof rating, and 20-hour battery life for outdoor adventures.",
        "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=600&h=400&fit=crop",
        19,
    ),
    _product(
        "ErgoFlex Office Chair",
        "Home Office",
        "Chair",
        299,
        "Ergonomic mesh office chair with adjustable lumbar support, headrest, and breathable fabric for all-day comfort.",
        "https://images.unsplash.com/photo-1592078615290-033ee584e267?w=600&h=400&fit=crop",
        6,
    ),
    _product(
        "SnapLens Mirrorless Camera",
        "Cameras",
        "Mirrorless",
        599,
        "Compact mirrorless camera with a 24MP sensor, 4K video, and fast autofocus for vlogging and street photography.",
        "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=600&h=400&fit=crop",
        5,
    ),
    _product(
        "FlexDesk Standing Desk",
        "Home Office",
        "Desk",
        449,
        "Electric height-adjustable standing desk with memory presets, cable management tray, and a spacious bamboo top.",
        "https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?w=600&h=400&fit=crop",
        7,
    ),
    _product(
        "Halo Over-Ear Studio Headphones",
        "Audio",
        "Headphones",
        209,
        "Studio-style headphones tuned for balanced sound, plush ear cushions, and long listening sessions.",
        "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&h=400&fit=crop",
        13,
    ),
    _product(
        "Drift ANC Travel Earbuds",
        "Audio",
        "Earbuds",
        119,
        "Compact travel earbuds with active noise cancellation, fast pairing, and a pocket charging case.",
        "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&h=400&fit=crop",
        20,
    ),
    _product(
        "Prism RGB Gaming Keyboard",
        "Gaming",
        "Keyboard",
        159,
        "Hot-swappable gaming keyboard with bright RGB effects, programmable macros, and smooth mechanical switches.",
        "https://images.unsplash.com/photo-1618384887929-16ec33fab9ef?w=600&h=400&fit=crop",
        10,
    ),
    _product(
        "Vector Pro Gaming Mouse",
        "Gaming",
        "Mouse",
        95,
        "Lightweight esports mouse with a high-precision sensor, adjustable DPI, and a braided cable.",
        "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=600&h=400&fit=crop",
        22,
    ),
    _product(
        "Titan Streaming Microphone",
        "Gaming",
        "Microphone",
        139,
        "USB condenser microphone with a clean voice pickup, mute button, and shock mount for streaming or podcasts.",
        "/media/shop/images/a5ed34c2bee8439581c27d6b8815ba95.jpg",
        11,
    ),
    _product(
        "Nebula 144Hz Gaming Monitor",
        "Gaming",
        "Monitor",
        279,
        "Fast 144Hz monitor with low input lag, vivid colors, and adaptive sync for competitive play.",
        "https://images.unsplash.com/photo-1545239351-1141bd82e8a6?w=600&h=400&fit=crop",
        9,
    ),
    _product(
        "Pixel Pro Webcam",
        "Computing",
        "Webcam",
        89,
        "Sharp 1080p webcam with autofocus, privacy shutter, and low-light correction for meetings and content creation.",
        "https://images.unsplash.com/photo-1593642532744-d377ab507dc8?w=600&h=400&fit=crop",
        18,
    ),
    _product(
        "Crest Bluetooth Keyboard",
        "Computing",
        "Keyboard",
        79,
        "Slim Bluetooth keyboard that pairs with laptops, tablets, and phones for flexible everyday typing.",
        "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&h=400&fit=crop",
        25,
    ),
    _product(
        "Arc Ergonomic Mouse",
        "Computing",
        "Mouse",
        65,
        "Comfort-first mouse with a vertical grip, precise tracking, and quiet clicks for long workdays.",
        "https://images.unsplash.com/photo-1527814050087-3793815479db?w=600&h=400&fit=crop",
        16,
    ),
    _product(
        "Orbit Laptop Dock",
        "Accessories",
        "Dock",
        129,
        "Single-cable laptop dock with HDMI, Ethernet, USB ports, and PD charging for a tidy desk setup.",
        "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=600&h=400&fit=crop",
        12,
    ),
    _product(
        "Cloud Carry Laptop Sleeve",
        "Accessories",
        "Sleeve",
        29,
        "Padded laptop sleeve with a soft lining, water-resistant shell, and a slim profile for daily commutes.",
        "https://images.unsplash.com/photo-1593642532871-8b12e02d091c?w=600&h=400&fit=crop",
        34,
    ),
    _product(
        "Stratus Power Bank",
        "Accessories",
        "Power Bank",
        49,
        "High-capacity power bank with fast charging, dual outputs, and enough power for long trips.",
        "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=600&h=400&fit=crop",
        23,
    ),
    _product(
        "Beacon Wireless Charger",
        "Accessories",
        "Charger",
        35,
        "Fast wireless charging pad with a non-slip finish and LED status indicator for desks and nightstands.",
        "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=600&h=400&fit=crop",
        27,
    ),
    _product(
        "Halo Desk Organizer",
        "Home Office",
        "Organizer",
        25,
        "Minimal desk organizer with compartments for pens, sticky notes, cables, and daily essentials.",
        "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=600&h=400&fit=crop",
        20,
    ),
    _product(
        "Nimbus Filing Tray",
        "Home Office",
        "Organizer",
        31,
        "Stackable filing tray that keeps documents, notebooks, and mail sorted in one neat place.",
        "https://images.unsplash.com/photo-1497366754035-f200968a6e72?w=600&h=400&fit=crop",
        14,
    ),
    _product(
        "Studio Drafting Lamp",
        "Home Office",
        "Lighting",
        74,
        "Adjustable LED lamp with a wide arm, focused beam, and touch controls for precise task lighting.",
        "https://images.unsplash.com/photo-1524758631624-e2822e304c36?w=600&h=400&fit=crop",
        8,
    ),
    _product(
        "Northstar Wireless Charger",
        "Home Office",
        "Accessories",
        42,
        "Desk-friendly wireless charging stand that keeps your phone visible while it powers up.",
        "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=600&h=400&fit=crop",
        19,
    ),
    _product(
        "Breeze Smart Air Cooler",
        "Home",
        "Cooling",
        189,
        "Compact room cooler with oscillation, timer controls, and quiet operation for summer comfort.",
        "https://images.unsplash.com/photo-1524758631624-e2822e304c36?w=600&h=400&fit=crop",
        11,
    ),
    _product(
        "Mist Aroma Diffuser",
        "Home",
        "Diffuser",
        37,
        "Ultrasonic diffuser with soothing mist, color night light, and automatic shutoff.",
        "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=600&h=400&fit=crop",
        29,
    ),
    _product(
        "QuietClean Robot Vacuum",
        "Home",
        "Vacuum",
        329,
        "Smart robot vacuum that maps rooms, avoids obstacles, and keeps floors tidy with minimal effort.",
        "/media/shop/images/a7b38d22834e420eafca1b734d38e421.jpg",
        6,
    ),
    _product(
        "Glow Smart Plug Kit",
        "Home",
        "Smart Home",
        54,
        "Two-pack smart plugs for scheduling lamps, fans, and other small appliances from your phone.",
        "https://images.unsplash.com/photo-1558002038-1055907df827?w=600&h=400&fit=crop",
        31,
    ),
    _product(
        "Frost Ceramic Heater",
        "Home",
        "Heater",
        89,
        "Portable ceramic heater with thermostat control, safety shutoff, and fast warm-up performance.",
        "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=600&h=400&fit=crop",
        13,
    ),
    _product(
        "Summit Action Camera",
        "Cameras",
        "Action Camera",
        239,
        "Adventure-ready action camera with electronic stabilization, waterproof housing, and crisp 4K capture.",
        "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=600&h=400&fit=crop",
        7,
    ),
    _product(
        "Aperture Compact Tripod",
        "Cameras",
        "Tripod",
        58,
        "Lightweight tripod with adjustable height, phone mount support, and stable legs for everyday shooting.",
        "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=600&h=400&fit=crop",
        22,
    ),
    _product(
        "FrameShot Camera Bag",
        "Cameras",
        "Bag",
        71,
        "Protective camera bag with padded dividers, quick-access pockets, and weather-resistant fabric.",
        "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=600&h=400&fit=crop",
        18,
    ),
    _product(
        "Luma Portrait Lens Kit",
        "Cameras",
        "Lens",
        419,
        "Portrait lens kit that delivers sharp subject separation, smooth background blur, and clean low-light results.",
        "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=600&h=400&fit=crop",
        4,
    ),
    _product(
        "Stride Fitness Band",
        "Fitness",
        "Band",
        49,
        "Resistance band set for strength training, stretching, and mobility work at home or on the go.",
        "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=600&h=400&fit=crop",
        28,
    ),
    _product(
        "ZenFlow Yoga Mat",
        "Fitness",
        "Mat",
        43,
        "Cushioned yoga mat with a grippy texture and extra length for balance, stretching, and floor workouts.",
        "https://images.unsplash.com/photo-1518611012118-696072aa579a?w=600&h=400&fit=crop",
        26,
    ),
    _product(
        "CorePulse Smart Scale",
        "Fitness",
        "Scale",
        59,
        "Bluetooth smart scale that tracks body weight and body composition trends in your companion app.",
        "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=600&h=400&fit=crop",
        15,
    ),
    _product(
        "Stride Pro Water Bottle",
        "Fitness",
        "Bottle",
        24,
        "Insulated water bottle that keeps drinks cold during workouts, hikes, and busy commutes.",
        "https://images.unsplash.com/photo-1517705008128-361805f42e86?w=600&h=400&fit=crop",
        33,
    ),
    _product(
        "Nomad Weekender Backpack",
        "Travel",
        "Backpack",
        84,
        "Carry-on friendly backpack with a laptop sleeve, organizer pockets, and a durable weather-resistant finish.",
        "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600&h=400&fit=crop",
        17,
    ),
    _product(
        "Voyage Carry-On Suitcase",
        "Travel",
        "Luggage",
        159,
        "Lightweight carry-on suitcase with smooth wheels, a telescoping handle, and a hard-shell exterior.",
        "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600&h=400&fit=crop",
        10,
    ),
    _product(
        "CloudRest Neck Pillow",
        "Travel",
        "Pillow",
        27,
        "Memory foam neck pillow that supports long flights and road trips with a soft, removable cover.",
        "https://images.unsplash.com/photo-1518611012118-696072aa579a?w=600&h=400&fit=crop",
        27,
    ),
    _product(
        "TrailSip Insulated Bottle",
        "Travel",
        "Bottle",
        29,
        "Leak-resistant insulated bottle designed to keep water cold through travel days and outdoor use.",
        "https://images.unsplash.com/photo-1517705008128-361805f42e86?w=600&h=400&fit=crop",
        24,
    ),
    _product(
        "BlendCraft Countertop Blender",
        "Kitchen",
        "Blender",
        119,
        "High-speed blender for smoothies, soups, and sauces with a sturdy jar and multiple speed settings.",
        "https://images.unsplash.com/photo-1570222094114-d054a817e56b?w=600&h=400&fit=crop",
        9,
    ),
    _product(
        "BrewStone Coffee Grinder",
        "Kitchen",
        "Grinder",
        67,
        "Compact burr grinder that gives coffee lovers a consistent grind for espresso or pour-over brewing.",
        "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=600&h=400&fit=crop",
        18,
    ),
    _product(
        "CrispAir Air Fryer",
        "Kitchen",
        "Air Fryer",
        109,
        "Easy-to-use air fryer with preset buttons, fast heating, and a roomy basket for everyday meals.",
        "https://images.unsplash.com/photo-1585515320310-259814833e62?w=600&h=400&fit=crop",
        12,
    ),
    _product(
        "CopperBoil Electric Kettle",
        "Kitchen",
        "Kettle",
        48,
        "Quick-boil electric kettle with an auto shutoff base and a clean stainless steel finish.",
        "https://images.unsplash.com/photo-1547592180-85f173990554?w=600&h=400&fit=crop",
        22,
    ),
    _product(
        "Luma Smart Bulb Pack",
        "Smart Home",
        "Lighting",
        39,
        "Color-changing smart bulb pair with app control, schedules, and voice assistant support.",
        "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=600&h=400&fit=crop",
        35,
    ),
    _product(
        "WatchTower Security Camera",
        "Smart Home",
        "Camera",
        79,
        "Indoor security camera with motion alerts, night vision, and live view from your phone.",
        "https://images.unsplash.com/photo-1558002038-1055907df827?w=600&h=400&fit=crop",
        16,
    ),
    _product(
        "EchoLink Voice Hub",
        "Smart Home",
        "Hub",
        129,
        "Voice-controlled smart home hub for music, reminders, weather, and connected devices.",
        "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=600&h=400&fit=crop",
        8,
    ),
    _product(
        "SecureView Video Doorbell",
        "Smart Home",
        "Doorbell",
        149,
        "Smart doorbell camera with two-way audio, motion detection, and mobile notifications.",
        "https://images.unsplash.com/photo-1558002038-1055907df827?w=600&h=400&fit=crop",
        11,
    ),
    _product(
        "SilkAir Hair Dryer",
        "Beauty",
        "Hair Dryer",
        89,
        "Fast-drying hair dryer with multiple heat settings, a cool shot button, and a lightweight body.",
        "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=600&h=400&fit=crop",
        20,
    ),
    _product(
        "GlossLine Hair Straightener",
        "Beauty",
        "Styling Tool",
        74,
        "Ceramic straightener that smooths hair quickly while helping reduce heat damage and frizz.",
        "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=600&h=400&fit=crop",
        14,
    ),
    _product(
        "PureGlow Facial Steamer",
        "Beauty",
        "Skincare",
        52,
        "Gentle facial steamer for at-home skincare routines, helping open pores and hydrate skin.",
        "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=600&h=400&fit=crop",
        17,
    ),
    _product(
        "TrimPro Grooming Kit",
        "Beauty",
        "Grooming",
        64,
        "All-in-one grooming kit with multiple attachments for beard, hair, and body trimming.",
        "https://images.unsplash.com/photo-1526378722484-bd91ca387e72?w=600&h=400&fit=crop",
        23,
    ),
    _product(
        "EcoSip Travel Mug",
        "Accessories",
        "Mug",
        21,
        "Leak-resistant travel mug that keeps coffee warm and fits comfortably in car cup holders.",
        "https://images.unsplash.com/photo-1517705008128-361805f42e86?w=600&h=400&fit=crop",
        29,
    ),
    _product(
        "Rover Portable Speaker",
        "Audio",
        "Speaker",
        95,
        "Rugged portable speaker with deep bass, Bluetooth pairing, and splash resistance for day trips.",
        "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=600&h=400&fit=crop",
        18,
    ),
    _product(
        "Edge Foldable Tablet Stand",
        "Accessories",
        "Stand",
        32,
        "Foldable stand for tablets and phones that makes video calls, watching, and reading more comfortable.",
        "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=600&h=400&fit=crop",
        31,
    ),
    _product(
        "Pulse Air Monitor",
        "Computing",
        "Monitor",
        289,
        "27-inch productivity monitor with slim bezels, sharp text rendering, and a clean matte finish.",
        "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=600&h=400&fit=crop",
        10,
    ),
    _product(
        "Harbor Leather Laptop Bag",
        "Accessories",
        "Bag",
        99,
        "Professional laptop bag with a padded compartment, polished finish, and room for daily essentials.",
        "https://images.unsplash.com/photo-1514477917009-389c76a86b68?w=600&h=400&fit=crop",
        12,
    ),
    _product(
        "Vista Desk Mat",
        "Home Office",
        "Accessories",
        27,
        "Large desk mat that protects your surface, keeps devices steady, and adds a clean workspace look.",
        "https://images.unsplash.com/photo-1593642532871-8b12e02d091c?w=600&h=400&fit=crop",
        25,
    ),
    _product(
        "Journey Noise-Canceling Neckbuds",
        "Audio",
        "Earbuds",
        132,
        "Lightweight neckband earbuds with active noise cancellation and long battery life for commuting.",
        "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&h=400&fit=crop",
        14,
    ),
    _product(
        "Summit Smart Scale Pro",
        "Fitness",
        "Scale",
        72,
        "Connected smart scale with body metrics tracking and clean, easy-to-read display.",
        "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=600&h=400&fit=crop",
        13,
    ),
]


class Command(BaseCommand):
    help = (
        "Clear all products and seed 50+ new products with properly matched "
        "Unsplash URLs and downloaded local image files."
    )

    def handle(self, *args, **options):
        Product.objects.all().delete()
        created = []
        errors = []

        for item in PRODUCTS:
            product = Product.objects.create(
                product_name=item["name"],
                category=item["category"],
                sub_category=item["sub_category"],
                price=item["price"],
                desc=item["desc"],
                pub_date=date.today(),
                image_url=item["image_url"],
                available_now=item["available_now"],
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
        if url.startswith("/media/"):
            source_path = os.path.join(settings.MEDIA_ROOT, url.removeprefix("/media/"))
            if not os.path.exists(source_path):
                raise FileNotFoundError(source_path)
            shutil.copyfile(source_path, tmp_path)
        else:
            urllib.request.urlretrieve(url, tmp_path)

        with open(tmp_path, "rb") as f:
            product.image.save(filename, File(f), save=True)

        os.remove(tmp_path)
