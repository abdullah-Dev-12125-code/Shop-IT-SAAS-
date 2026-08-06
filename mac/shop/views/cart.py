import json
from decimal import Decimal, InvalidOperation
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods



@ensure_csrf_cookie
@login_required
def checkout(request):
    return render(request, 'shop/checkout.html')

@ensure_csrf_cookie
@login_required
def cart(request):
    return render(request, 'shop/cart.html')

