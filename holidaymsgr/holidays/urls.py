from django.conf.urls import patterns, include, url

from . import views


urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^message.html$', views.message, name='message'),
    url(r'^message/$', views.message, name='message'),
)

