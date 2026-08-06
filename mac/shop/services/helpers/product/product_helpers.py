from collections import Counter, defaultdict
from django.utils.text import slugify
from ....models import Product, Order
import json



# Limits for homepage sections.
HOT_SELLING_LIMIT = 8
RECENT_ORDERS_FOR_TRENDING = 50



# Groups products by category and splits them into slides
# of 3 products each (used for carousel rendering).
# Returns:
# [
#   ("Electronics", [[p1,p2,p3], [p4,p5,p6]]),
#   ("Fashion", [[...]])
# ]


def group_products_by_category(products):
    grouped = defaultdict(list)

    for product in products:
        grouped[product.category].append(product)

    allprods = []

    for cat, items in grouped.items():
        slides = [items[i:i + 3] for i in range(0, len(items), 3)]
        allprods.append((cat, slides))

    return allprods



# Builds the category navigation bar.
# Also inserts an "All Products" category at the beginning.

def build_categories(products):
    names = {
        p.category
        for p in products
        if p.category
    }

    categories = [
        {
            "name": name,
            "slug": slugify(name),
            "icon": CATEGORY_ICONS.get(name.lower(), "tag"),
        }
        for name in sorted(names)
    ] 

    categories.insert(
        0,
        {
            "name": "All Products",
            "slug": "all",
            "icon": "shopping-cart",
        }
    )

    return categories



# Reads the item_json stored in an order and yields:
#
# ("12", 2)
# ("44", 1)
#
# Supports both:
# {"12":2}
#
# and
#
# [{"id":12,"qty":2}]

def iter_order_line_items(raw_item_json):
    try:
        items = json.loads(raw_item_json or "[]")
    except (json.JSONDecodeError, TypeError):
        return

    if isinstance(items, dict):
        iterator = items.items()

    elif isinstance(items, list):
        iterator = (
            (entry.get("id"), entry.get("qty", 1))
            for entry in items
            if isinstance(entry, dict)
        )

    else:
        return

    for product_id, qty in iterator:
        if product_id is None:
            continue

        try:
            qty = int(qty)
        except (TypeError, ValueError):
            qty = 1

        yield str(product_id), qty



# Counts how many times every product has been purchased.
# Returns the Product objects ordered by sales count.

def ranked_products_from_orders(item_json_values, limit):
    product_sales = Counter()

    for item_json in item_json_values:
        for product_id, quantity in iter_order_line_items(item_json):
            product_sales[product_id] += quantity

    if not product_sales:
        return []

    ranked_ids = [
        int(product_id)
        for product_id, _ in product_sales.most_common(limit)
        if product_id.isdigit()
    ]

    products = Product.objects.in_bulk(ranked_ids)

    return [
        products[product_id]
        for product_id in ranked_ids
        if product_id in products
    ]



# Returns the top-selling products from recent orders.

def hot_selling_products(orders, limit=HOT_SELLING_LIMIT):
    return ranked_products_from_orders(
        orders.values_list("item_json", flat=True),
        limit,
    )



# Builds every piece of data required by index.html.
#
# Responsibilities:
# • Filter category
# • Compute hot-selling products
# • Remove featured products from discover section
# • Sort by rating if "interest" mode is enabled
# • Return template context

def build_home_context(products, query=None, category_slug=None, interest=False):
    products = list(products)

    # Filter products by selected category.
    if category_slug and category_slug != "all":
        products = [
            p
            for p in products
            if slugify(p.category) == category_slug
        ]

    # Find best-selling products using recent orders.
    hot_selling = hot_selling_products(
        Order.objects.order_by("-created_at")[:RECENT_ORDERS_FOR_TRENDING]
    )

    # IDs already shown in the featured section.
    featured_ids = {
        p.id
        for p in hot_selling
    }

    # Remaining products go into Discover.
    discover_products = [
        p
        for p in products
        if p.id not in featured_ids
    ]

    # Optional sorting by rating.
    if interest:
        discover_products.sort(
            key=lambda p: (
                getattr(p, "rating", 0) or 0,
                p.id,
            ),
            reverse=True,
        )

    return {
        "allprods": group_products_by_category(products),
        "categories": build_categories(Product.objects.all()),
        "hot_selling": hot_selling,
        "festival_name": "Eid-ul-Adha Specials",
        "discover_products": discover_products,
        "query": query,
    }



# Maps category names to Lucide icon names.
# Used by the homepage category navigation.

CATEGORY_ICONS = {
    "computing": "laptop",
    "electronics": "plug",
    "gaming": "gamepad-2",
    "school": "school",
    "school accessories": "backpack",
    "books": "book-open",
    "stationery": "pen",
    "fashion": "shopping-bag",
    "men": "user",
    "women": "user-round",
    "kids": "baby",
    "shoes": "footprints",
    "accessories": "glasses",
    "watches": "watch",
    "jewelry": "gem",
    "beauty": "sparkles",
    "health": "heart-pulse",
    "fitness": "dumbbell",
    "sports": "trophy",
    "toys": "toy-brick",
    "baby": "baby",
    "home": "house",
    "home & living": "sofa",
    "furniture": "armchair",
    "kitchen": "utensils",
    "appliances": "blender",
    "groceries": "shopping-cart",
    "food": "pizza",
    "drinks": "cup-soda",
    "pets": "paw-print",
    "automotive": "car",
    "motorcycles": "bike",
    "tools": "wrench",
    "office": "briefcase",
    "garden": "sprout",
    "travel": "plane",
    "luggage": "luggage",
    "phones": "smartphone",
    "computers": "monitor",
    "cameras": "camera",
    "audio": "headphones",
    "music": "music",
    "movies": "film",
    "software": "code-2",
    "gifts": "gift",
    "art": "palette",
    "crafts": "scissors",
    "medical": "stethoscope",
    "other": "package",
}