from django.shortcuts import render
from django.db.models import Q
from django.views.decorators.csrf import ensure_csrf_cookie
from ..models import Product, Order
from django.core.cache import cache
from ..services import build_home_context

@ensure_csrf_cookie
def home(request):
    category_slug = request.GET.get("category")
    interest = request.GET.get("interest") == "1"

    cache_key = f"home_{category_slug}_{interest}"

    context = cache.get(cache_key)
    
    if context is None:
        context = build_home_context(
        Product.objects.all(),
        category_slug=category_slug,
        interest=interest,
        )
        cache.set(cache_key, context, 300)       
    
    return render(request, "shop/index.html", context)


index = home
shops = home
categories = home


# Search: Takes input -> tokenize -> match -> return    
def search(request):
    query = (request.GET.get('search') or '').strip()
    category_slug = request.GET.get('category')
    interest = request.GET.get('interest') == '1'
    products = Product.objects.all()

    if query:
        query_words = query.lower().split()
        search_filter = Q()

        for word in query_words:
            search_filter &= (
                Q(product_name__icontains=word)
                | Q(category__icontains=word)
                | Q(sub_category__icontains=word)
                | Q(desc__icontains=word)
            )

        products = products.filter(search_filter)

    context = build_home_context(products, query=query, category_slug=category_slug, interest=interest)
    return render(request, 'shop/index.html', context)

def searchMatch(query, item):
    if not query:
        return True
    
    query_words = query.lower().strip().split()

    searchable_text = " ".join([
        item.product_name,
        item.category,
        item.sub_category,
        item.desc,
    ]).lower()

    return all(word in searchable_text for word in query_words)
