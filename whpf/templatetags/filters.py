from django import template
import json

register = template.Library()


@register.filter
def tojson(value):
    j = json.dumps(value)
    return j


@register.filter
def get_domain_url(request):
    return request.build_absolute_uri('/')


@register.filter
def get_user_info(user):
    social = user.social_auth.get()
    backend = social.get_backend().name
    url = ''
    icon_class = ''
    if backend == 'twitter':
        screen_name = social.extra_data['access_token']['screen_name']
        url = "http://www.twitter.com/%s" % screen_name
        icon_class = 'fa fa-twitter'

    if backend == 'facebook':
        fid = social.extra_data['id']
        url = "http://www.facebook.com/%s" % fid
        icon_class = 'fa fa-facebook'

    if backend == 'reddit':
        username = social.extra_data['username']
        url = "http://www.reddit.com/u/%s" % username
        icon_class = 'fa fa-reddit-alien'

    if backend == 'google-oauth2':
        url = ''
        icon_class = 'fa fa-google'

    return {'url': url, 'icon_class': icon_class, }
