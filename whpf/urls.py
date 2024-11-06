# coding=utf-8
from django.urls import path

from graphene_django.views import GraphQLView

from . import views

app_name = "whpf"

urlpatterns = [
    path("", views.home, name="home"),
    path("tv/", views.tv, name="tv"),
    path("faq/", views.faq, name="faq"),
    path("save/<str:code>/", views.save, name="save"),
    path("results/<str:code>/", views.results, name="results"),
    path("scoreboard/", views.scoreboard, name="scoreboard"),
    path("score/<str:code>/", views.score, name="score"),
    path("stats/", views.stats, name="stats"),
    path("stats/<str:team_code>/", views.stats_team, name="stats_team"),
    path("right_guess/<int:pid>/", views.right_guess, name="right_guess"),
    path("wrong_guess/<int:pid>/", views.wrong_guess, name="wrong_guess"),
    path("graphql", GraphQLView.as_view(graphiql=True)),
]
