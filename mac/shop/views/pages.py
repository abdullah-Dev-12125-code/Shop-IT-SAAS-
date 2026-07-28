from django.shortcuts import render
from ..models import Contact

def about(request):
    return render(request, 'shop/about.html')


def contact(request):
    thank = False
    if request.method == "POST":
        name = request.POST.get('name','')
        email = request.POST.get('email','')
        phone = request.POST.get('phone','')
        message = request.POST.get('message','')
       
        contact = Contact(name=name, email=email, phone_number=phone, desc=message)
        Contact.save(contact)
        thank = True
    return render(request, 'shop/contact.html',{'thank': thank})