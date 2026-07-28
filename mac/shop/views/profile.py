from django.shortcuts import render
from django.contrib.auth.decorators import login_required



@login_required
def profile(request):
    user = 'abdullah'
    return render(request, 'shop/profile.html', {"user": user})
