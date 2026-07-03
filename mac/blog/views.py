from django.shortcuts import render, redirect # type: ignore
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse # type: ignore
from .models import Blogpost, CustomUser

def login_view(request):
    if request.method == 'POST':
        email = request.POST["email"]
        password = request.POST["password"]

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect("/accounts/login/")
        else:
            return render(request, "login.html", {"error": "Invalid Credentials"})
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect("/accounts/login/")


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("/blog/")

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")

        if not email or not username or not password or not password2:
            return render(request, "registration/signup.html", {"error": "All fields are required."})

        if password != password2:
            return render(request, "registration/signup.html", {"error": "Passwords do not match."})

        if CustomUser.objects.filter(email=email).exists():
            return render(request, "registration/signup.html", {"error": "An account with this email already exists."})

        if CustomUser.objects.filter(username=username).exists():
            return render(request, "registration/signup.html", {"error": "Username is already taken."})

        CustomUser.objects.create_user(email=email, username=username, password=password)
        messages.success(request, "Account created successfully. Please log in.")
        return redirect("/accounts/login/")

    return render(request, "registration/signup.html")





@login_required
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
    prevpost = Blogpost.objects.filter(post_id__lt=post.post_id).order_by('-post_id').first()
    nextpost = Blogpost.objects.filter(post_id__gt=post.post_id).order_by('post_id').first()

    context = {'post': post,
               'prev': prevpost,
               'next': nextpost
               }
    return render(request, 'blog/post_view.html', context)

def pub_blog(request):
    if request.method == 'POST':
        title = request.POST.get('title','')
        head1 = request.POST.get('head1','')
        cont1 = request.POST.get('cont1','')
        head2 = request.POST.get('head2','')
        cont2 = request.POST.get('cont2','')
        head3 = request.POST.get('head3','')
        cont3 = request.POST.get('cont3','')
        habout = request.POST.get('hab','')
        cabout = request.POST.get('cabout','')
        github_link = request.POST.get('GitHub','')
        twitter = request.POST.get('twitter','')
        facebook = request.POST.get('facebook','')
        imageUpload = request.FILES.get('imageUpload','')
        blog = Blogpost(title=title, 
                        head0=head1, chead0=cont1, 
                        head1=head2, chead1=cont2, 
                        head2=head3, chead2=cont3, 
                        about_title=habout, about_content=cabout, 
                        github_link=github_link, facebook_link = facebook, twitter_link = twitter, 
                        thumbnail=imageUpload)
        blog.save()
        
    return render(request, 'blog/publish_blog.html')
