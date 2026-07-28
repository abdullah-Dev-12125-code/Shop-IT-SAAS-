from django.shortcuts import render
from ..models import Product



def product(request,id):
    context = { 'product': Product.objects.get(id = id) } 
    return render(request, 'shop/product.html', context)