# coding=utf-8
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^tv/$', views.tv, name='tv'),
    url(r'^results/(?P<code>\w+)/$', views.results, name='results'),
]
