"""urlconf for the base application"""

from django.conf.urls import url, patterns
from views import *

urlpatterns = patterns('base.views',
    url(r'^auth/(?P<hmac>[\w]+)/(?P<email>.+)$', AuthView.as_view(), name='auth'),
    url(r'^invalid-auth/?$', InvalidAuthView.as_view(), name='invalid-auth'),
)
