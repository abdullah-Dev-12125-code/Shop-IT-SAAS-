import json
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from ..models import Order, OrderItem, OrderUpdate, Product



@login_required
def orders(request):
    orders = Order.objects.filter(
        Q(user=request.user) | Q(email_linked=request.user.email)
    ).order_by('-created_at')

    return render(request, 'shop/orders.html', {'orders': orders})

@login_required
def order_list(request):
    orders = Order.objects.filter(
        Q(user=request.user) | Q(email_linked=request.user.email)
    ).order_by('-created_at')

    return render(request, 'shop/orders.html', {"orders": orders})

