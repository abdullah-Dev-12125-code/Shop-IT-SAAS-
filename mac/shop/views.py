from django.shortcuts import render
from collections import defaultdict
from .models import Product, Contact 


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


def shops(request):
    return render(request, 'shop/shops.html')


def categories(request):
    return render(request, 'shop/categories.html')


def about(request):
    return render(request, 'shop/about.html')


def contact(request):
    if request.method == "POST":
        name = request.POST.get('name','')
        email = request.POST.get('email','')
        phone = request.POST.get('phone','')
        message = request.POST.get('message','')
        contact = Contact(name=name, email=email, phone_number=phone, desc=message)
        Contact.save(contact)
    return render(request, 'shop/contact.html')


def tracker(request):
    return render(request, 'shop/tracker.html')


def search(request):
    return render("We are search")


def product(request,id):
    context = { 'product': Product.objects.get(id = id) } 
    return render(request, 'shop/product.html', context)


def checkout(request):
    return render(request,"shop/checkout.html")


def cart(request):
    return render(request, 'shop/cart.html')
