# Django settings for holidaymsgr project.

import sys  # @UnusedImport
import os  # @UnusedImport

###############################################################################
###############################################################################
## THESE THINGS YOU SHOULD SET IN PRODUCTION OR BAD THINGS WILL HAPPEN
###############################################################################
###############################################################################

DEBUG = True

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/London'

# The fully qualified hostname of the sieve server
SIEVE_SERVER = "imap.example.com"

# Make this unique, and don't share it with anybody.
SECRET_KEY = '*ivd!%8j-=7r36ng^)rmeto(wj)#9)ylzd_hhrzv#x%+a)gs8x'

SESSION_COOKIE_AGE = 3600

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# Details for the Apache configuration
WEBSERVER = {
    "SERVER_NAME": "www.example.com",
    "ACCESS_LOG": "/path/to/access_log",
    "ERROR_LOG": "/path/to/error_log",
    "SSL": {
        "CERT": "/path/to/certificate.crt",
        "KEY": "/path/to/key.key",
        "CHAIN": "/path/to/chainfile.crt",
    }
}

GUNICORN = {
    "USER": "daemon",
    "ACCESS_LOG": "/path/to/access_log",
    "ERROR_LOG": "/path/to/error_log",
    "PORT": "8000",
}

###############################################################################
###############################################################################
## THESE THINGS YOU *CAN* CHANGE
###############################################################################
###############################################################################


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

###############################################################################
###############################################################################
## THESE THINGS YOU CANNOT CHANGE. THEY ARE APPLICATION CONFIGURATION.
###############################################################################
###############################################################################

from json_settings import *  # @UnusedWildImport

# This is autocalculated. The script is written by setup.py
GUNICORN['COMMAND'] = os.path.join(sys.prefix, "bin", "django")

TEMPLATE_DEBUG = DEBUG

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'holidaymsgr.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'holidaymsgr.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    os.path.join(os.path.dirname(__file__), "..", "templates")
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'stackhelper',
    'json_settings',
    'gunicorn',
    'holidaymsgr.holidays',
)

SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'
