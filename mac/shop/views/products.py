from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import ensure_csrf_cookie
from ..models import Product



@ensure_csrf_cookie
def product(request,id):
    context = { 'product': get_object_or_404(Product.objects.select_related('seller'), id=id) }
    return render(request, 'shop/product.html', context)