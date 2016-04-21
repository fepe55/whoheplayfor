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
