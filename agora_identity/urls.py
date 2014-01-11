""" Default urlconf for agora_identity """

from django.conf.urls import include, patterns, url
from django.conf import settings

urlpatterns = patterns('',
    url(r'', include('base.urls')),
)

if settings.DEBUG:
    from django.contrib import admin
    admin.autodiscover()

    urlpatterns += patterns('',
        url(r'^admin/', include(admin.site.urls)),
    )