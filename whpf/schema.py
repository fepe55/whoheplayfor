import graphene
from graphene_django import DjangoObjectType

from .models import Team, Player


class TeamType(DjangoObjectType):
    class Meta:
        model = Team
        fields = ('city', 'name')


class PlayerType(DjangoObjectType):
    class Meta:
        model = Player
        fields = ('name', 'active', 'team')


class Query(graphene.ObjectType):
    all_players = graphene.List(PlayerType)
    team_by_name = graphene.Field(
        TeamType,
        name=graphene.String(required=True)
    )

    def resolve_all_players(root, info):
        return Player.objects.select_related('team').all()

    def resolve_team_by_name(root, info, name):
        try:
            return Team.objects.get(name=name)
        except Team.DoesNotExist:
            return None


schema = graphene.Schema(query=Query)
