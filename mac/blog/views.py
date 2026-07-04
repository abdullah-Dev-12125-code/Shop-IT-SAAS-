from django.shortcuts import render # type: ignore
from django.contrib.auth.decorators import login_required
from .models import Blogpost

@login_required(login_url='/accounts/login/')
def index(request):
    posts = Blogpost.objects.all()
    return render(request, 'blog/index.html', {'posts': posts})

@login_required(login_url='/accounts/login/')
def contact(request):
    thank = False
    if request.method == 'POST':
        thank = True

    return render(request, 'blog/contact.html', {'thank': thank})

@login_required(login_url='/accounts/login/')
def post_view(request, id):
    post = Blogpost.objects.get(post_id=id)
    prevpost = Blogpost.objects.filter(post_id__lt=post.post_id).order_by('-post_id').first()
    nextpost = Blogpost.objects.filter(post_id__gt=post.post_id).order_by('post_id').first()

    context = {
        'post': post,
        'prev': prevpost,
        'next': nextpost,
    }
    return render(request, 'blog/post_view.html', context)

@login_required(login_url='/accounts/login/')
def pub_blog(request):
    if request.method == 'POST':
        title = request.POST.get('title', '')
        head1 = request.POST.get('head1', '')
        cont1 = request.POST.get('cont1', '')
        head2 = request.POST.get('head2', '')
        cont2 = request.POST.get('cont2', '')
        head3 = request.POST.get('head3', '')
        cont3 = request.POST.get('cont3', '')
        habout = request.POST.get('hab', '')
        cabout = request.POST.get('cabout', '')
        github_link = request.POST.get('GitHub', '')
        twitter = request.POST.get('twitter', '')
        facebook = request.POST.get('facebook', '')
        imageUpload = request.FILES.get('imageUpload', '')
        blog = Blogpost(
            title=title,
            head0=head1,
            chead0=cont1,
            head1=head2,
            chead1=cont2,
            head2=head3,
            chead2=cont3,
            about_title=habout,
            about_content=cabout,
            github_link=github_link,
            facebook_link=facebook,
            twitter_link=twitter,
            thumbnail=imageUpload,
        )
        blog.save()

    return render(request, 'blog/publish_blog.html')
