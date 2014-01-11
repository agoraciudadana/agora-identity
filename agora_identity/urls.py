""" Default urlconf for agora_identity """

from django.conf.urls import include, patterns, url
from django.conf import settings

urlpatterns = patterns('',
    url(r'%s' % settings.LOCATION_SUBPATH, include('base.urls')),
)

if settings.DEBUG:
    from django.contrib import admin
    admin.autodiscover()

    urlpatterns += patterns('',
        url(r'^%sadmin/' % settings.LOCATION_SUBPATH, include(admin.site.urls)),
    )