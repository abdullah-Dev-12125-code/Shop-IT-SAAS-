from collections import Counter, defaultdict
from django.shortcuts import render
from django.utils.text import slugify
from ..models import Product, Order
from django.core.cache import cache
import json


def home(request):
    category_slug = request.GET.get("category")
    interest = request.GET.get("interest") == "1"

    cache_key = f"home_{category_slug}_{interest}"

    context = cache.get(cache_key)
    
    if context is None:
        context = _build_home_context(
        Product.objects.all(),
        category_slug=category_slug,
        interest=interest,
        )
        cache.set(cache_key, context, 300)       
    
    return render(request, "shop/index.html", context)


index = home
shops = home
categories = home


# Search: Takes input -> tokenize -> match -> return    
def search(request):
    query = (request.GET.get('search') or '').strip()
    category_slug = request.GET.get('category')
    interest = request.GET.get('interest') == '1'
    products = Product.objects.all()

    if query:
        products = [product for product in products if searchMatch(query, product)]

    context = _build_home_context(products, query=query, category_slug=category_slug, interest=interest)
    return render(request, 'shop/index.html', context)

def searchMatch(query, item):
    if not query:
        return True
    
    query_words = query.lower().strip().split()

    searchable_text = " ".join([
        item.product_name,
        item.category,
        item.sub_category,
        item.desc,
    ]).lower()

    return all(word in searchable_text for word in query_words)



FESTIVAL_KEYWORDS = ["eid", "bakra eid", "qurbani", "festival", "ramadan"]

HOT_SELLING_LIMIT = 8
FESTIVAL_LIMIT = 8
RECENT_ORDERS_FOR_TRENDING = 50




def _group_products_by_category(products):
    grouped = defaultdict(list)

    for product in products:
        grouped[product.category].append(product)

    allprods = []
    for cat, items in grouped.items():
        slides = [items[i:i + 3] for i in range(0, len(items), 3)]
        allprods.append((cat, slides))

    return allprods


def _build_categories(products):
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

    categories.insert(0, {
        "name": "All Products",
        "slug": "all",
        "icon": "shopping-cart",
    })

    return categories

def _iter_order_line_items(raw_item_json):
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

def _ranked_products_from_orders(item_json_values, limit):
    product_sales = Counter()

    for item_json in item_json_values:
        for product_id, quantity in _iter_order_line_items(item_json):
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




def _hot_selling_products(orders, limit=HOT_SELLING_LIMIT):
    return _ranked_products_from_orders(
        orders.values_list("item_json", flat=True),
        limit,
    )



def _festival_products(products, limit=FESTIVAL_LIMIT):
    matches = []

    for product in products:
        haystack = " ".join(
            filter(None, [
                product.category, 
                product.sub_category, 
                product.desc,
                ])

        ).lower()

        if any(keyword in haystack for keyword in FESTIVAL_KEYWORDS):
            matches.append(product)

            if len(matches) >= limit:
                break

    return matches



def _build_home_context(products, query=None, category_slug=None, interest=False):
    products = list(products)

    # Category filtering
    # "all" means show every product
    if category_slug and category_slug != "all":
        products = [
            p for p in products
            if slugify(p.category) == category_slug
        ]

    hot_selling = _hot_selling_products(Order.objects.order_by("-created_at")[:RECENT_ORDERS_FOR_TRENDING])
    festival_products = _festival_products(products)

    featured_ids = (
        {p.id for p in hot_selling}
        | {p.id for p in festival_products}
    )

    discover_products = [
        p for p in products
        if p.id not in featured_ids
    ]

    if interest:
        discover_products.sort(
            key=lambda p: (
                getattr(p, "rating", 0) or 0,
                p.id
            ),
            reverse=True,
        )

    return {
        "allprods": _group_products_by_category(products),

        # Category list with All Products included
        "categories": _build_categories(Product.objects.all()),

        "hot_selling": hot_selling,
        "festival_products": festival_products,
        "festival_name": "Eid-ul-Adha Specials",
        "discover_products": discover_products,
        "query": query,
    }





# Purely cosmetic: an icon per category slug for the sub-nav pills. Any
# category not listed here just falls back to a generic tag icon, so new
# categories in the catalog never break the nav.
# SVG icon names from Lucide Icons
# https://lucide.dev/
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