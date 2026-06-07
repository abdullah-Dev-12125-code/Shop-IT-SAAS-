from django.shortcuts import render
from collections import defaultdict
from .models import Product


def index(request):
    products = Product.objects.all()
    grouped = defaultdict(list)

    for p in products:
        grouped[p.category].append(p)


    allprods = []

    for cat,items in grouped.items():


        slides = [
            items[i:i + 4] for i in range(0, len(items), 4)
            ]

        allprods.append((cat, slides))

    params = {
        'allprods': allprods
    }

    return render(request, 'shop/index.html', params)

def about(request):
    return render(request, 'shop/about.html')

def contact(request):
    return render("We are contact")

def tracker(request):
    return render("We are tracker")

def search(request):
    return render("We are search")

def prod(request):
    return render("I am the product")

def checkout(request):
    return render("I am the checkout")

def products(request):
    context = {
        'product': Product.objects.all()
    }
    return render(request, 'shop/product.html', context)





