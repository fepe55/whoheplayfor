"""WhoHePlayFor URL Configuration"""
from django.contrib import admin
from django.urls import (path, include, )
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', include('social_django.urls', namespace='social')),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('djadmin/', admin.site.urls),
    path('', include('whpf.urls', namespace="whpf")),
]
