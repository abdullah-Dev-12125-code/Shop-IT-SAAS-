from django.db import models
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..models import Order, Product, OrderUpdate
from django.http import JsonResponse
import json


@login_required
def tracker(request):
    if request.method == "POST":
        orderid = request.POST.get('orderid', 0)
        email = request.POST.get('email', '')

        try:
            order = Order.objects.filter(id=orderid, email_linked=email)

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
