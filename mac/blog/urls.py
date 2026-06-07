from django.contrib import admin # pyright: ignore[reportMissingModuleSource]
from django.urls import path # type: ignore
from . import views


urlpatterns = [
    path('', views.index,name="blogHome"),
]