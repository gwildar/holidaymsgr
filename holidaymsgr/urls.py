from django.conf.urls import patterns, include, url
from .holidays import urls

urlpatterns = patterns('',
    url('', include(urls, namespace="holidays")),
)

