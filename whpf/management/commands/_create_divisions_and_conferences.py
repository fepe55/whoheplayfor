# coding=utf-8
from django.core.management.base import BaseCommand

from whpf.models import (Conference, Division, )


class Command(BaseCommand):
    help = 'Creates conferences and divisions'

    def handle(self, *args, **kwargs):
        east = Conference.objects.create(name='East')
        west = Conference.objects.create(name='West')

        Division.objects.create(name='Atlantic', conference=east)
        Division.objects.create(name='Central', conference=east)
        Division.objects.create(name='Southeast', conference=east)

        Division.objects.create(name='Northwest', conference=west)
        Division.objects.create(name='Pacific', conference=west)
        Division.objects.create(name='Southwest', conference=west)

        # return
