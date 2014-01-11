# -*- coding: utf-8 -*-
"""
This is an example settings/local.py file.
These settings overrides what's in settings/base.py
"""

from . import base
from django.utils.translation import ugettext_lazy as _

# To extend any settings from settings/base.py here's an example.
# If you don't need to extend any settings from base.py, you do not need
# to import base above
INSTALLED_APPS = base.INSTALLED_APPS + (
    'django_nose',
    'djcelery_email',
)

CELERY_EMAIL_TASK_CONFIG = {
    'queue' : 'email',
    'rate_limit' : '180/m',
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db/development.sqlite3',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
        #'OPTIONS': {
        #    'init_command': 'SET storage_engine=InnoDB',
        #    'charset' : 'utf8',
        #    'use_unicode' : True,
        #},
        #'TEST_CHARSET': 'utf8',
        #'TEST_COLLATION': 'utf8_general_ci',
    },
    # 'slave': {
    #     ...
    # },
}

# Recipients of traceback emails and other notifications.
ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)
MANAGERS = ADMINS

EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'

CELERY_EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# SECURITY WARNING: don't run with debug turned on in production!
# Debugging displays nice error messages, but leaks memory. Set this to False
# on all server instances and True only for development.
DEBUG = TEMPLATE_DEBUG = True

# Is this a development instance? Set this to True on development/master
# instances and False on stage/prod.
DEV = True

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# SECURITY WARNING: keep the secret key used in production secret!
# Hardcoded values can leak through source control. Consider loading
# the secret key from an environment variable or a file instead.
SECRET_KEY = 'vn&%k*rr)#kh7x$2l_q2m2!k!t-t=k%k!9(aa8l4y*6ld3=@7v'

# Uncomment these to activate and customize Celery:
# CELERY_ALWAYS_EAGER = False  # required to activate celeryd
# BROKER_HOST = 'localhost'
# BROKER_PORT = 5672
# BROKER_USER = 'django'
# BROKER_PASSWORD = 'django'
# BROKER_VHOST = 'django'
# CELERY_RESULT_BACKEND = 'amqp'

## Log settings

# Remove this configuration variable to use your custom logging configuration
LOGGING_CONFIG = None
LOGGING = {
    'version': 1,
    'loggers': {
        'agora_identity': {
            'level': "DEBUG"
        }
    }
}

INTERNAL_IPS = ('127.0.0.1')

ALLOW_SEND_MAILS = True

SEND_MAILS_PASSWORD = 'change this password'

LOGIN_HMAC_SECRET = 'change this'

LOGIN_HMAC_SALT = 'change this too'

AGORA_LINK = 'https://agora.confederacionpirata.org'

AGORA_SECRET = 'shared secret change this too'

AGORA_API_KEY = '<user>:<apikey>'

BASE_USERNAME = 'user'

NUM_RANDOM_USERNAME_CHARS = 5

SITE_NAME = 'Elige tus eurodiputados #primariasPiratas'

EVENT_TITLE = 'Elige tus eurodiputados #primariasPiratas'

EVENT_TEXT = (
    'Te hemos enviado un correo con este enlace para facilitarte el acceso al '
    'sistema de votación. Para poder participar de esta forma, debes primero '
    'facilitarnos algunos datos identificativos. El voto, será secreto y '
    'contará con importantes medidas de seguridad.')

TOS_TITLE = (
    'Acepta la política de privacidad y las condiciones de uso')

TOS_TEXT = (
    "Lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum "
    "lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum "
    "lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum "
    "lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum "
    "lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum "
    "lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum ")

# Allows to put agora-identity in a subpath instead of needing a subdomain
LOCATION_SUBPATH = ""

# allow to use basic auth when connecting to the agora api
AGORA_BASIC_AUTH = None
