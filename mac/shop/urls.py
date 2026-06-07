from django.contrib import admin # type: ignore
from django.urls import path # type: ignore
from . import views


urlpatterns = [
    
path('', views.index, name="shop"),
path('about/', views.about, name="AboutUs"),
path('contact/',views.contact, name="ContactUs"),
path('tracker/',views.tracker, name="TrackUs"),
path('search/',views.search, name="search"),
path('products/',views.prod, name="products"),
path('checkout/',views.checkout, name="CheckOut"),
path('product/',views.products,name="productsLIsting")
]

