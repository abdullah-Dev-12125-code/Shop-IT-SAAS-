import json
from decimal import Decimal, InvalidOperation

from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods


CART_SESSION_KEY = "shop_cart"


def _normalize_cart(cart):
    normalized = []

    if not isinstance(cart, list):
        return normalized

    for item in cart:
        if not isinstance(item, dict):
            continue

        try:
            quantity = int(item.get("qty", 1))
        except (TypeError, ValueError):
            quantity = 1

        if quantity <= 0:
            quantity = 1

        try:
            price = Decimal(str(item.get("price", 0)))
        except (InvalidOperation, TypeError, ValueError):
            price = Decimal("0.00")

        normalized.append({
            "id": item.get("id"),
            "name": str(item.get("name", "Item")),
            "price": float(price),
            "qty": quantity,
            "image": item.get("image", "") or "",
        })

    return normalized


def _session_cart(request):
    return _normalize_cart(request.session.get(CART_SESSION_KEY, []))


def _store_session_cart(request, cart):
    request.session[CART_SESSION_KEY] = _normalize_cart(cart)
    request.session.modified = True


@ensure_csrf_cookie
@require_http_methods(["GET", "POST"])
def cart_api(request):
    if request.method == "GET":
        cart = _session_cart(request)
        return JsonResponse({
            "success": True,
            "cart": cart,
            "count": sum(item["qty"] for item in cart),
            "total_price": sum((Decimal(str(item["price"])) * item["qty"] for item in cart), Decimal("0.00")),
        })

    try:
        data = json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid cart payload"}, status=400)

    cart = data.get("cart", [])
    _store_session_cart(request, cart)
    stored_cart = _session_cart(request)

    return JsonResponse({
        "success": True,
        "cart": stored_cart,
        "count": sum(item["qty"] for item in stored_cart),
        "total_price": sum((Decimal(str(item["price"])) * item["qty"] for item in stored_cart), Decimal("0.00")),
    })




@ensure_csrf_cookie
@login_required
def checkout(request):
    return render(request, 'shop/checkout.html')

@ensure_csrf_cookie
@login_required
def cart(request):
    return render(request, 'shop/cart.html')

