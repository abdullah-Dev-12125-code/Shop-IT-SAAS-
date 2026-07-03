from django.contrib import admin  # pyright: ignore[reportMissingModuleSource]
from django.urls import path, include  # type: ignore
from django.conf import settings
from django.conf.urls.static import static
from . import views
from blog import views as blog_views

urlpatterns = [
    path('', views.index),
    path('admin/', admin.site.urls),
    path('accounts/signup/', blog_views.signup_view, name='signup'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('blog/', include("blog.urls")),
    path('shop/', include("shop.urls"))


]

# ✅ DEBUG TOOLBAR (IMPORTANT FIX)
if settings.DEBUG:
    import debug_toolbar # type: ignore
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

# media files
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)