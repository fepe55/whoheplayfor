import pytest
from django.contrib.auth.models import User

from whpf.helpers import get_score
from whpf.models import Conference, Division, Player, Result, Team


@pytest.fixture
def code():
    # This code corresponds to
    # {
    #     "hard_mode": False,
    #     "show_player_name": True,
    #     "shuffle_teams": False,
    #     "time_left": 8,
    #     "time_limit": 60,
    #     "rounds_played": 20,
    #     "total_rounds": 20,
    #     "guesses": "01630526626000201609616100101150373700203471383801629003555501628970666600201949515100202693484801630217636301630543445400203924656501630257395301629726643800203486666601627774505000203095525201627732555500202734605301628973424201629631373736326",  # noqa: E501
    #     "limit_teams": 0,
    # }
    # The guesses are based on an existing game, we should make them match a fixture with teams and players
    return (
        "v001010000080600200200163052662600020160961610010115037370020347"
        "1383801629003555501628970666600201949515100202693484801630217636"
        "3016305434454002039246565016302573953016297266438002034866666016"
        "2777450500020309552520162773255550020273460530162897342420162963"
        "1373736326"
    )


@pytest.fixture
def user():
    """Fixture to create a user for the tests."""
    return User.objects.create_user(username="testuser", password="password123")


@pytest.fixture
def create_conferences_and_divisions():
    east, _ = Conference.objects.get_or_create(name="East")
    west, _ = Conference.objects.get_or_create(name="West")

    atlantic, _ = Division.objects.get_or_create(name="Atlantic", conference=east)
    central, _ = Division.objects.get_or_create(name="Central", conference=east)
    southeast, _ = Division.objects.get_or_create(name="Southeast", conference=east)

    northwest, _ = Division.objects.get_or_create(name="Northwest", conference=west)
    pacific, _ = Division.objects.get_or_create(name="Pacific", conference=west)
    southwest, _ = Division.objects.get_or_create(name="Southwest", conference=west)


@pytest.fixture
def create_players(create_conferences_and_divisions):
    team = Team.objects.create(
        nba_id=1,
        city="Test City",
        name="Test Team",
        abbreviation="TST",
        code="test_team",
        division=Division.objects.get(name="Atlantic"),
    )
    Player.objects.create(
        nba_id=1,
        name="Test Player",
        team=team,
        code="test_player",
    )


@pytest.fixture
def results_fixture(user, code):
    """Fixture to create multiple Result instances for testing."""
    results = [
        Result.objects.create(user=user, score=get_score(code), code=code),
        Result.objects.create(user=user, score=get_score(code), code=code),
        Result.objects.create(user=user, score=get_score(code), code=code),
    ]
    other_user = User.objects.create_user(username="another_user", password="password123")
    results.append(Result.objects.create(user=other_user, score=get_score(code), code=code))

    return results
