from functools import wraps

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render

from .forms import SellerLoginForm, SellerRegisterForm
from .models import Seller


User = get_user_model()


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
    return render(request, "seller/dashboard.html")


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