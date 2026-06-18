from django.contrib import admin # type: ignore
from django.urls import path # type: ignore
from . import views


urlpatterns = [
path('', views.index, name="home"),
path('index/', views.index, name="shop"),
path('shops/', views.shops, name="shops"),
path('categories/', views.categories, name="categories"),
path('about/', views.about, name="AboutUs"),
path('contact/',views.contact, name="contact"),
path('tracker/',views.tracker, name="TrackUs"),
path('search/',views.search, name="search"),
path('checkout/',views.checkout, name="CheckOut"),
path('product/<int:id>/',views.product,name="product"),
path('cart/',views.cart,name='cart'),
path('checkout/',views.checkout,name="checkout")
]

