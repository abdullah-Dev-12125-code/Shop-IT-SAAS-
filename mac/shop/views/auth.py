from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect



def signup_user(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        errors = None

        if not username:
            errors = "The username field is required"

        elif not email:
            errors = "The email field is required"

        elif not password1:
            errors = "The password field is empty"

        elif not password2:
            errors = "The confirmation password is empty"

        elif password1 != password2:
            errors = "Passwords do not match"

        elif User.objects.filter(username=username).exists():
            errors = "Username already exists"

        elif User.objects.filter(email=email).exists():
            errors = "Email already exists"

        if errors:
            return render(
                request,
                "shop/signup.html",
                {"error": errors}
            )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        login(request, user)

        return redirect("shop:shop")

    return render(request, "shop/signup.html")


def login_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)
        
        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            user_obj = None

        if user_obj:
            user = authenticate(request, username=user_obj.username, password=password)

            if user is not None:
                login(request, user)
                return redirect('shop:shop')

        return render(request, 'shop/login.html', {'error': 'Invalid email or password.'})
    
    return render(request, 'shop/login.html')

def forgot_pass(request):
    return render(request, 'shop/forgot.html')

def verification(request):
    return render(request, 'shop/acc_verification.html')

def logout_user(request):
    logout(request)
    return redirect('shop:login')