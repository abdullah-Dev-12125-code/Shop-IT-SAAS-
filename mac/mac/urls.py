from django.conf.urls.static import static
from django.urls import path, include  # type: ignore
from django.conf import settings
from django.contrib import admin  # pyright: ignore[reportMissingModuleSource]




urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("shop.urls")),
    path('seller/', include("seller.urls")),
]

















# ✅ DEBUG TOOLBAR (IMPORTANT FIX)
if settings.DEBUG:
    import debug_toolbar # type: ignore
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

# media files
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)