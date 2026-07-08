from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
import json
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.text import slugify
from .models import Contact, Order, OrderUpdate, Product
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.method == 'POST':
        username = request.get['username']
        password = request.get['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('shop:index')
        
        return render(request, 'shop/login.html', {'error':'Invalid Credentials'})
    
    return render(request, 'shop/login.html') 


def logout_view(request):
    logout(request)
    return redirect(request, 'shop:login')




# Purely cosmetic: an icon per category slug for the sub-nav pills. Any
# category not listed here just falls back to a generic tag icon, so new
# categories in the catalog never break the nav.
CATEGORY_ICONS = {
    "electronics": "💻",
    "gaming": "🎮",
    "school accessories": "🎒",
    "school": "🎒",
    "fashion": "👕",
    "home & living": "🏠",
    "home": "🏠",
    "beauty": "💄",
    "sports": "🏸",
}

# Interim way to flag "festival" products until Product has a dedicated
# tag/boolean field for this. Matched (case-insensitively) against category,
# sub_category and desc. Extend this list for other seasons/sales.
FESTIVAL_KEYWORDS = ["eid", "bakra eid", "qurbani", "festival", "ramadan"]

HOT_SELLING_LIMIT = 8
TOP_PURCHASED_LIMIT = 8
FESTIVAL_LIMIT = 8
RECENT_ORDERS_FOR_TRENDING = 50


def _normalize_cart_items(cart):
    normalized = []
    total_price = Decimal("0.00")

    if not isinstance(cart, list):
        return normalized, total_price
    
    product_ids = [
        item.get("id")
        for item in cart
        if isinstance(item, dict) and item.get("id") is not None
    ]

    products = Product.objects.in_bulk(product_ids)


    for raw_item in cart:
        if not isinstance(raw_item, dict):
            continue

        product_id = raw_item.get("id")
        try:
            quantity = int(raw_item.get("qty", 1))
        except (TypeError, ValueError):
            quantity = 1

        if quantity <= 0:
            quantity = 1

        product = products.get(product_id)

        if product:
            item_name = product.product_name
            item_price = Decimal(str(product.price))
            item_image = product.image_url or (product.image.url if product.has_image_file else "")
        else:
            item_name = str(raw_item.get("name", "Item"))
            try:
                item_price = Decimal(str(raw_item.get("price", 0)))
            except (InvalidOperation, TypeError, ValueError):
                item_price = Decimal("0.00")
            item_image = raw_item.get("image", "") or ""

        normalized.append({
            "id": product_id,
            "name": item_name,
            "price": float(item_price),
            "qty": quantity,
            "image": item_image,
        })
        total_price += item_price * quantity

    return normalized, total_price


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
    """Distinct categories -> [{'name', 'slug', 'icon'}, ...] for the sub-nav."""

    names = {
        product.category
        for product in products
        if product.category
    }

    categories = [
        {
            "name": name,
            "slug": slugify(name),
            "icon": CATEGORY_ICONS.get(name.lower(), "🛍"),
        }
        for name in sorted(names)
    ]

    # Add All Products option at the top
    categories.insert(0, {
        "name": "All Products",
        "slug": "all",
        "icon": "🛒",
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
    counts = Counter()

    for raw_item_json in item_json_values:
        for product_id, qty in _iter_order_line_items(raw_item_json):
            counts[product_id] += qty

    if not counts:
        return []

    ranked_ids = [
        int(pid)
        for pid, _ in counts.most_common(limit)
        if pid.isdigit()
    ]

    products = Product.objects.in_bulk(ranked_ids)

    return [
        products[pid]
        for pid in ranked_ids
        if pid in products
    ]


def _top_purchased_products(limit=TOP_PURCHASED_LIMIT):
    return _ranked_products_from_orders(
        Order.objects.values_list("item_json", flat=True),
        limit,
    )

def _hot_selling_products(
    limit=HOT_SELLING_LIMIT,
    recent_orders=RECENT_ORDERS_FOR_TRENDING,
):
    return _ranked_products_from_orders(
        Order.objects.order_by("-created_at")
        .values_list("item_json", flat=True)[:recent_orders],
        limit,
    )



def _festival_products(products, limit=FESTIVAL_LIMIT):
    matches = []

    for product in products:
        haystack = " ".join(
            filter(None, [product.category, product.sub_category, product.desc])
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

    hot_selling = _hot_selling_products()
    if not hot_selling:
        hot_selling = products[:HOT_SELLING_LIMIT]

    top_purchased = _top_purchased_products()
    if not top_purchased:
        fallback_start = HOT_SELLING_LIMIT
        top_purchased = products[fallback_start:fallback_start + TOP_PURCHASED_LIMIT]
        if not top_purchased:
            top_purchased = products[:TOP_PURCHASED_LIMIT]

    festival_products = _festival_products(products)

    featured_ids = (
        {p.id for p in hot_selling}
        | {p.id for p in top_purchased}
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
        "top_purchased": top_purchased,
        "festival_products": festival_products,
        "festival_name": "Eid-ul-Adha Specials",
        "discover_products": discover_products,
        "query": query,
    }



@login_required
def index(request):
    category_slug = request.GET.get('category')
    interest = request.GET.get('interest') == '1'
    context = _build_home_context(Product.objects.all(), category_slug=category_slug, interest=interest)
    return render(request, 'shop/index.html', context)


def shops(request):
    category_slug = request.GET.get('category')
    interest = request.GET.get('interest') == '1'
    context = _build_home_context(Product.objects.all(), category_slug=category_slug, interest=interest)
    return render(request, 'shop/index.html', context)


def categories(request):
    category_slug = request.GET.get('category')
    interest = request.GET.get('interest') == '1'
    context = _build_home_context(Product.objects.all(), category_slug=category_slug, interest=interest)
    return render(request, 'shop/index.html', context)


def tracker(request):
    if request.method == "POST":
        orderid = request.POST.get('orderid', 0)
        email = request.POST.get('email', '')

        try:
            order = Order.objects.filter(id=orderid, email=email)

            if not order.exists():
                return JsonResponse({
                    "success": False,
                    "message": "Order not found"
                })

            order_obj = order.first()

            # SAFE JSON LOAD
            try:
                raw_items = json.loads(order_obj.item_json)
            except:
                raw_items = []

            items = []

            # CASE 1: dict format {id: qty}
            if isinstance(raw_items, dict):

                for product_id, qty in raw_items.items():
                    product = Product.objects.filter(id=product_id).first()

                    items.append({
                        "name": product.product_name if product else "Unknown Product",
                        "qty": qty,
                        "id": product_id
                    })

            # CASE 2: list format [{id: , qty: }]
            elif isinstance(raw_items, list):

                for item in raw_items:
                    product_id = item.get("id")
                    qty = item.get("qty", 1)

                    product = Product.objects.filter(id=product_id).first()

                    items.append({
                        "name": product.product_name if product else "Unknown Product",
                        "qty": qty,
                        "id": product_id
                    })

            # ORDER UPDATES
            updates_qs = OrderUpdate.objects.filter(order_id=orderid)

            updates = []
            for item in updates_qs:
                updates.append({
                    "text": item.update_desc,
                    "time": item.timestamp.strftime("%Y-%m-%d %H:%M")
                })

            return JsonResponse({
                "success": True,
                "update": updates,
                "items": items
            })

        except Exception as e:
            return JsonResponse({
                "success": False,
                "message": str(e)
            })

    return render(request, 'shop/tracker.html')


def create_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body or b"{}")
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid request payload"}, status=400)

        cart = data.get("cart", [])
        normalized_cart, server_total = _normalize_cart_items(cart)

        if not normalized_cart:
            return JsonResponse({"success": False, "error": "Your cart is empty"}, status=400)

        order = Order.objects.create(
            first_name = data["first_name"],
            last_name = data["last_name"],
            email = data["email"],
            phone = data["phone"],
            address = data["address"],
            city = data["city"],
            zip_code = data["zip_code"],
            country = data["country"],
            payment_method = data["payment_method"],
            total_price = server_total,
            item_json = json.dumps(normalized_cart),
        
        )

        update = OrderUpdate.objects.create(
        order_id=order.id,
        update_desc="The order has been placed" 
        
        )
        update.save()
    

        return JsonResponse({
            "success": True,
            "order_id": order.id,
            "total_price": str(server_total)
        })

    return JsonResponse({"success":False, "error": "Invalid request method"}, status=405)    


def about(request):
    return render(request, 'shop/about.html')


def contact(request):
    thank = False
    if request.method == "POST":
        name = request.POST.get('name','')
        email = request.POST.get('email','')
        phone = request.POST.get('phone','')
        message = request.POST.get('message','')
       
        contact = Contact(name=name, email=email, phone_number=phone, desc=message)
        Contact.save(contact)
        thank = True
    return render(request, 'shop/contact.html',{'thank': thank})

def product(request,id):
    context = { 'product': Product.objects.get(id = id) } 
    return render(request, 'shop/product.html', context)


def checkout(request):
    return render(request, 'shop/checkout.html')


def cart(request):
    return render(request, 'shop/cart.html')

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


def search(request):
    query = (request.GET.get('search') or '').strip()
    category_slug = request.GET.get('category')
    interest = request.GET.get('interest') == '1'
    products = Product.objects.all()

    if query:
        products = [product for product in products if searchMatch(query, product)]

    context = _build_home_context(products, query=query, category_slug=category_slug, interest=interest)
    return render(request, 'shop/index.html', context)