from django.contrib import admin # pyright: ignore[reportMissingModuleSource]
from django.urls import path # type: ignore
from . import views

app_name = "blog"

urlpatterns = [
    path('', views.index, name="blog"),
    path('contact/', views.contact, name="contact"),
    path('post/<int:id>',views.post_view,name="post_view"),
    path('publish/',views.pub_blog, name='publish_blog')
]