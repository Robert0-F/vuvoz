"""
URL configuration for vuvoz project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path

from .views import VueSPAView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('collection.urls')),
]

# Media must be registered before the SPA catch-all, otherwise /media/* returns index.html.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    from django.views.static import serve

    urlpatterns += [
        re_path(
            r'^media/(?P<path>.*)$',
            serve,
            {'document_root': settings.MEDIA_ROOT},
        ),
    ]

urlpatterns += [
    re_path(r'^', VueSPAView.as_view()),
]
