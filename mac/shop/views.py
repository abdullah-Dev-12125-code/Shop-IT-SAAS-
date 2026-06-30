from django.shortcuts import render
from collections import defaultdict
from .models import Product, Contact, Order, OrderUpdate
from django.http import JsonResponse, HttpResponse
import json

def index(request):
    products = Product.objects.all()
    grouped = defaultdict(list)
    
    for p in products:
        grouped[p.category].append(p)
    print("image.url:", p.image.url)

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
    return render(request, 'shop/index.html')


def categories(request):
    return render(request, 'shop/index.html')



from django.shortcuts import render
from django.http import JsonResponse
from .models import Order, OrderUpdate, Product
import json

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
        data = json.loads(request.body)
        cart = data.get("cart", []) 

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
            total_price = data["total_price"],
            item_json = json.dumps(cart),
        
        )

        update = OrderUpdate.objects.create(
        order_id=order.id,
        update_desc="The order has been placed" 
        
        )
        update.save()
    

        return JsonResponse({
            "success": True,
            "order_id": order.id
        })

    return JsonResponse({"success":False})    


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
    return render(request,"shop/checkout.html")


def cart(request):
    return render(request, 'shop/cart.html')




