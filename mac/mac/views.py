#This file is created by me 
from django.shortcuts import render # type: ignore
from django.http import HttpResponse # type: ignore 




def index(request):
    return render(request, 'mac/index.html')
