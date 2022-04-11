from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# import debug_toolbar

from app_marketplace.views import ClearCacheAdminView

urlpatterns = [
    path('admin/clearcache/', ClearCacheAdminView.as_view(),
         name="clearcache_admin"),
    path('admin/', admin.site.urls),
    path('account/', include('app_users.urls')),
    path('', include('app_marketplace.urls')),
    path('', include('pay_api.urls')),
    # path('__debug__/', include(debug_toolbar.urls)),
    path('i18n', include('django.conf.urls.i18n')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
