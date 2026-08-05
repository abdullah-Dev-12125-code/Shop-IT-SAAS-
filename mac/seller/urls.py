from django.urls import path
from . import views

app_name = "vendor"

urlpatterns = [
    path('dashboard/', views.dashboard, name='dash'),
    path('sign-up/', views.signup_seller, name="signup"),
    path('login/', views.login_seller, name="login"),
    path('logout/', views.logout_seller, name="logout"),
]
