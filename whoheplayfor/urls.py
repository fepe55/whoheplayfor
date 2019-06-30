"""WhoHePlayFor URL Configuration"""
# from django.contrib import admin
from django.urls import (path, include, )

urlpatterns = [
    path('', include('social.apps.django_app.urls', namespace='social')),
    path('', include('django.contrib.auth.urls')),
    # path('admin/', admin.site.urls),
    path('', include('whpf.urls', namespace="whpf")),
]
