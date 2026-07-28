import json

from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from ..models import Order, OrderUpdate, Product



@login_required
def orders(request):
    return render(request, 'shop/orders.html')

def order_list(request):
    orders = Order.objects.filter(email_linked=request.user.email)

    return render(request, 'shop/orders.html', {"orders": orders})




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



@login_required
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


@login_required
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
            email_linked = request.user.email
        
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
