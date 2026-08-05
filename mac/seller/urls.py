from django.urls import path
from . import views

app_name = "vendor"

urlpatterns = [
    path('dashboard/', views.dashboard, name='dash'),
    path('sign-up/', views.signup_seller, name="signup"),
    path('login/', views.login_seller, name="login"),
    path('logout/', views.logout_seller, name="logout"),
    path('products/', views.product_list, name='product-list'),
    path('products/add/', views.product_create, name='product-create'),
    path('products/<int:pk>/edit/', views.product_update, name='product-update'),
    path('products/<int:pk>/delete/', views.product_delete, name='product-delete'),
    path('orders/', views.seller_orders, name='seller-orders'),
]
