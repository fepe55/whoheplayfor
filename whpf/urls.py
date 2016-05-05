# coding=utf-8
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^tv/$', views.tv, name='tv'),
    url(r'^faq/$', views.faq, name='faq'),
    url(r'^save/(?P<code>\w+)/$', views.save, name='save'),
    url(r'^results/(?P<code>\w+)/$', views.results, name='results'),
    url(r'^scoreboard/$', views.scoreboard, name='scoreboard'),
    url(r'^score/(?P<code>\w+)/$', views.score, name='score'),
    url(r'^right_guess/(?P<pid>\w+)/$', views.right_guess, name='right_guess'),
    url(r'^wrong_guess/(?P<pid>\w+)/$', views.wrong_guess, name='wrong_guess'),
]
