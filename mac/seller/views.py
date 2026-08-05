from functools import wraps
from datetime import date
from decimal import Decimal
import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Count, Sum
from django.db.models.functions import Coalesce, TruncMonth
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import SellerLoginForm, SellerProductForm, SellerRegisterForm
from .models import Seller
from shop.models import Order, OrderItem, Product


User = get_user_model()


def _shift_month(year, month, offset):
    total = year * 12 + (month - 1) + offset
    shifted_year, shifted_month_index = divmod(total, 12)
    return shifted_year, shifted_month_index + 1


def seller_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("vendor:login")

        seller = getattr(request.user, "seller_profile", None)
        if seller is None:
            return redirect("vendor:login")

        if not seller.is_active:
            return HttpResponseForbidden("Seller account is inactive.")

        return view_func(request, *args, **kwargs)

    return _wrapped_view


@seller_required
def dashboard(request):
    seller = request.user.seller_profile
    products = Product.objects.filter(seller=seller).order_by("-pub_date")
    product_count = products.count()
    low_stock_products = list(products.filter(available_now__gt=0, available_now__lte=5).order_by("available_now", "product_name"))
    out_of_stock_products = list(products.filter(available_now__lte=0).order_by("product_name"))
    inventory_value = sum((product.price or 0) * (product.available_now or 0) for product in products)

    seller_orders = (
        OrderItem.objects.filter(product__seller=seller).select_related("order", "product").order_by("-order__created_at", "-id")
    )

    recent_order_items = list(seller_orders[:6])
    recent_orders = (
        seller_orders.values("order_id")
        .distinct()
    )

    order_ids = [row["order_id"] for row in recent_orders]
    recent_orders_data = list(
        OrderItem.objects.filter(order_id__in=order_ids)
        .select_related("order", "product")
        .order_by("-order__created_at", "-id")
    )

    order_queryset = Order.objects.filter(items__product__seller=seller).distinct()
    total_orders = order_queryset.count()
    total_revenue = order_queryset.aggregate(total=Coalesce(Sum("total_price"), Decimal("0.00")))["total"] or Decimal("0.00")
    total_customers = order_queryset.values("email").distinct().count()
    repeat_customers = (
        order_queryset.values("email")
        .annotate(order_count=Count("id", distinct=True))
        .filter(order_count__gt=1)
        .count()
    )
    repeat_customer_rate = int((repeat_customers / total_customers) * 100) if total_customers else 0
    new_customer_rate = 100 - repeat_customer_rate if total_customers else 0
    avg_order_value = (total_revenue / total_orders) if total_orders else Decimal("0.00")

    top_products = list(
        products.annotate(
            total_sold=Coalesce(Sum("order_items__quantity"), 0),
            total_revenue=Coalesce(Sum("order_items__line_total"), Decimal("0.00")),
        ).order_by("-total_revenue", "-total_sold", "product_name")[:5]
    )

    top_product_share = 0
    if top_products and total_revenue:
        top_product_share = int((top_products[0].total_revenue / total_revenue) * 100) if total_revenue else 0

    current_day = timezone.localdate()
    monthly_totals = {}
    six_month_sales = []
    for offset in range(-5, 1):
        year, month = _shift_month(current_day.year, current_day.month, offset)
        month_start = date(year, month, 1)
        next_year, next_month = _shift_month(year, month, 1)
        month_end = date(next_year, next_month, 1)

        monthly_total = (
            seller_orders
            .filter(order__created_at__date__gte=month_start, order__created_at__date__lt=month_end)
            .aggregate(total=Coalesce(Sum("line_total"), Decimal("0.00")))
            ["total"]
        )
        monthly_totals[month_start] = monthly_total or Decimal("0.00")

    max_month_value = max(monthly_totals.values()) if monthly_totals else Decimal("0.00")
    for offset in range(-5, 1):
        year, month = _shift_month(current_day.year, current_day.month, offset)
        month_start = date(year, month, 1)
        month_value = monthly_totals.get(month_start, Decimal("0.00"))
        six_month_sales.append({
            "label": month_start.strftime("%b"),
            "value": float(month_value),
            "value_display": f"PKR {month_value:,.0f}",
            "height": int((month_value / max_month_value) * 100) if max_month_value else 0,
            "highlight": month_start.month == current_day.month,
        })

    return render(request, "seller/dashboard.html", {
        "seller_products": products,
        "seller_profile": seller,
        "product_count": product_count,
        "low_stock_count": len(low_stock_products),
        "out_of_stock_count": len(out_of_stock_products),
        "inventory_value": inventory_value,
        "low_stock_products": low_stock_products,
        "out_of_stock_products": out_of_stock_products,
        "recent_order_items": recent_order_items,
        "recent_orders_data": recent_orders_data,
        "top_products": top_products,
        "sales_chart": six_month_sales,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "total_customers": total_customers,
        "repeat_customers": repeat_customers,
        "repeat_customer_rate": repeat_customer_rate,
        "new_customer_rate": new_customer_rate,
        "avg_order_value": avg_order_value,
        "top_product_share": top_product_share,
        "sales_chart_json": json.dumps(six_month_sales),
    })


@seller_required
def product_list(request):
    seller = request.user.seller_profile
    products = Product.objects.filter(seller=seller).order_by("-pub_date")
    return render(request, "seller/products/list.html", {"products": products})


@seller_required
def product_create(request):
    seller = request.user.seller_profile

    if request.method == "POST":
        form = SellerProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = seller
            product.save()
            messages.success(request, "Product created successfully.")
            return redirect("vendor:product-list")
    else:
        form = SellerProductForm()

    return render(request, "seller/products/form.html", {
        "form": form,
        "page_title": "Add Product",
    })


@seller_required
def product_update(request, pk):
    seller = request.user.seller_profile
    product = get_object_or_404(Product, pk=pk, seller=seller)

    if request.method == "POST":
        form = SellerProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully.")
            return redirect("vendor:product-list")
    else:
        form = SellerProductForm(instance=product)

    return render(request, "seller/products/form.html", {
        "form": form,
        "page_title": "Edit Product",
        "product": product,
    })


@seller_required
def product_delete(request, pk):
    seller = request.user.seller_profile
    product = get_object_or_404(Product, pk=pk, seller=seller)

    if request.method == "POST":
        product.delete()
        messages.success(request, "Product deleted successfully.")
        return redirect("vendor:product-list")

    return render(request, "seller/products/confirm_delete.html", {"product": product})


@seller_required
def seller_orders(request):
    seller = request.user.seller_profile
    order_items = (
        OrderItem.objects
        .select_related("order", "product")
        .filter(product__seller=seller)
        .order_by("-order__created_at", "-id")
    )
    return render(request, "seller/orders/list.html", {"order_items": order_items})


def login_seller(request):
    seller_profile = getattr(request.user, "seller_profile", None) if request.user.is_authenticated else None
    if seller_profile is not None and seller_profile.is_active:
        return redirect("vendor:dash")

    form = SellerLoginForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        identifier = form.cleaned_data["username"].strip()
        password = form.cleaned_data["password"]
        remember = form.cleaned_data.get("remember", False)

        user = authenticate(request, username=identifier, password=password)

        if user is None and "@" in identifier:
            try:
                user_obj = User.objects.get(email__iexact=identifier)
            except User.DoesNotExist:
                user_obj = None

            if user_obj is not None:
                user = authenticate(request, username=user_obj.username, password=password)

        if user is None:
            form.add_error(None, "Invalid seller credentials.")
        else:
            seller = getattr(user, "seller_profile", None)
            if seller is None:
                form.add_error(None, "No seller profile exists for this account.")
            elif not seller.is_active:
                form.add_error(None, "Your seller account is inactive.")
            else:
                login(request, user)
                if remember:
                    request.session.set_expiry(1209600)
                else:
                    request.session.set_expiry(0)
                return redirect("vendor:dash")

    return render(request, "seller/login_seller.html", {"form": form})


def signup_seller(request):
    if request.method == "POST":
        form = SellerRegisterForm(request.POST)

        if form.is_valid():
            seller = form.save()
            login(request, seller.user)
            request.session.set_expiry(0)
            return redirect("vendor:dash")
    else:
        form = SellerRegisterForm()

    return render(request, "seller/signup_seller.html", {"form": form})


def logout_seller(request):
    logout(request)
    return redirect("vendor:login")