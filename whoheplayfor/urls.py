"""WhoHePlayFor URL Configuration"""
from django.contrib import admin
from django.urls import (path, include, )

urlpatterns = [
    path('', include('social_django.urls', namespace='social')),
    path('', include('django.contrib.auth.urls')),
    path('djadmin/', admin.site.urls),
    path('', include('whpf.urls', namespace="whpf")),
]
