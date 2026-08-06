from django.contrib import admin # type: ignore
from django.urls import path # type: ignore
from .services import cart_api, create_order
from . import views


app_name = "shop"

urlpatterns = [
path('', views.index, name="home"),
path('index/', views.index, name="shop"),
path('shops/', views.shops, name="shops"),
path('categories/', views.categories, name="categories"),
path('about/', views.about, name="AboutUs"),
path('contact/',views.contact, name="contact"),
path('tracker/',views.tracker, name="TrackUs"),
path('search/',views.search, name="search"),
path('product/<int:id>/',views.product,name="product"),
path('cart/',views.cart,name='cart'),
path('cart/api/', cart_api, name='cart-api'),
path('checkout/',views.checkout,name="checkout"),
path('api/create-order/',create_order, name="create-order"),
path('signup/', views.signup_user, name="signup"),
path('login/', views.login_user, name="login"),
path('logout/', views.logout_user, name="logout"),
path('forgot/', views.forgot_pass, name="forgot"),
path('verify/', views.verification, name="verification"),
path('orders/', views.orders, name="orders"),
path('order-list', views.order_list, name="order-list"),
path('profile/', views.profile_view, name='profile'),
path('profile/edit/', views.edit_profile_view, name='edit_profile'),
path('profile/password/', views.change_password_view, name='change_password'),
]

