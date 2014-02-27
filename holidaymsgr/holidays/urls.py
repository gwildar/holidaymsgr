from django.conf import settings
from django.conf.urls import patterns
from django.conf.urls import url

from holidaymsgr.holidays import views
from holidaymsgr.holidays import views_testing


urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^message$', views.message, name='message'),
)


if settings.DEBUG:
    urlpatterns.extend(patterns('',
        url(r'^test$', views_testing.test_view, name='testing'),
        url(r'^test_login$', views_testing.test_login, name='test_login'),
    ))
