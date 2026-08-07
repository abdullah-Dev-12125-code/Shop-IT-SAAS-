import json
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from ..models import Order, OrderItem, OrderUpdate, Product
from django.core.cache import cache


@login_required
def orders(request):
    cache_key = f"orders_{request.user.id}"

    context = cache.get(cache_key)

    if context is None:
        orders = Order.objects.filter(
        Q(user=request.user) | Q(email_linked=request.user.email)
        ).prefetch_related(
            "items__product",
            "updates",
        ).order_by('-created_at')

        context = {"orders": orders}

        cache.set(cache_key, context, 300)
        


    return render(request, 'shop/orders.html', context)


def order_details(request, id):
    order = get_object_or_404(
        Order,
        Q(user=request.user) |
        Q(email_linked=request.user.email),
        id=id
    )

    order_items = OrderItem.objects.filter(order=order)

    updates = OrderUpdate.objects.filter(order=order).order_by("-timestamp")

    context = {    
        "order": order,    
        "order_items": order_items,  
        "updates": updates
        } 
    
    return render(request, "shop/order_info.html", context)
