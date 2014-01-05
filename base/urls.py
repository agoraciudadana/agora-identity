"""urlconf for the base application"""

from django.conf.urls import url, patterns, include
from views import *

urlpatterns = patterns('base.views',
    url(r'^auth/(?P<hmac>[0-9a-f]{40})/(?P<email>.+)$', AuthView.as_view(), name='auth'),
    url(r'^invalid-auth/?$', InvalidAuthView.as_view(), name='invalid-auth'),
)

if settings.ALLOW_SEND_MAILS:
    urlpatterns += patterns('base.views',
        url(r'^sendmails/?$', SendMailsView.as_view(), name='send-mails'),
        url(r'^captcha/', include('captcha.urls')),
        url(r'^sendmails/success/?$', SendMailsSuccessView.as_view(), name='send-mails-success'),
    )