from unittest.mock import MagicMock

import pytest

from whpf.templatetags.filters import get_user_info


@pytest.mark.parametrize(
    "provider, extra_data, expected_url, expected_icon_class",
    [
        ("twitter", {"access_token": {"screen_name": "testuser"}}, "https://www.twitter.com/testuser", "fa fa-twitter"),
        ("facebook", {"id": "123456"}, "https://www.facebook.com/123456", "fa fa-facebook"),
        ("reddit", {"username": "reddit_user"}, "https://www.reddit.com/u/reddit_user", "fa fa-reddit-alien"),
        ("google-oauth2", {}, "", "fa fa-google"),
    ],
)
def test_get_user_info(provider, extra_data, expected_url, expected_icon_class):
    """Test get_user_info for different social media providers."""

    # Create a mock user and social_auth object
    user = MagicMock()
    social_auth = MagicMock()
    user.social_auth.get.return_value = social_auth  # Mock the social_auth.get() method

    # Mock the social_auth instance's properties based on provider
    social_auth.provider = provider
    social_auth.extra_data = extra_data

    result = get_user_info(user)

    assert result == {"url": expected_url, "icon_class": expected_icon_class}
