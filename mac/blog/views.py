from django.shortcuts import render # type: ignore
from django.http import HttpResponse # type: ignore
from .models import Blogpost

# Create your views here.

def index(request):
    posts = Blogpost.objects.all()
    
    return render(request, 'blog/index.html', {'posts': posts})

def contact(request):
    thank = False
    if request.method == 'POST':
        thank = True

    return render(request, 'blog/contact.html', {'thank':thank})

def post_view(request,id):
    post = Blogpost.objects.get(post_id=id)
    
    return render(request, 'blog/post_view.html', {'post': post})

def pub_blog(request):
    if request.method == 'POST':
        title = request.POST.get('title','')
        head1 = request.POST.get('head1','')
        cont1 = request.POST.get('cont1','')
        head2 = request.POST.get('head2','')
        cont2 = request.POST.get('cont2','')
        head3 = request.POST.get('head3','')
        cont3 = request.POST.get('cont3','')
        imageUpload = request.FILES.get('imageUpload','')
        blog = Blogpost(title=title, head0=head1, chead0=cont1, head1=head2, chead1=cont2, head2=head3, chead2=cont3, thumbnail=imageUpload)
        blog.save()
        
    return render(request, 'blog/publish_blog.html')
