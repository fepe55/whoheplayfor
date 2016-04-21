"""WhoHePlayFor URL Configuration"""
from django.contrib import admin
from django.conf.urls import (url, include, )

urlpatterns = [
    url('', include('social.apps.django_app.urls', namespace='social')),
    url('', include('django.contrib.auth.urls', namespace='auth')),
    url(r'^admin/', admin.site.urls),
    url(r'^', include('whpf.urls', namespace="whpf")),

]
