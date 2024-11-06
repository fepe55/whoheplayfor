# coding=utf-8
from django.utils import formats

from .models import Options


def last_roster_update(request):
    options = Options.objects.all()
    last_update = ""
    if options.exists():
        last_update = formats.date_format(options.get().last_roster_update, "F jS, Y")

    return {"last_roster_update": last_update}
