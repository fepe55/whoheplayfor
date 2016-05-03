# coding=utf-8
from django.core.management.base import BaseCommand
from whpf.models import Result


class Command(BaseCommand):
    help = 'Recalculates every score'

    def handle(self, *args, **kwargs):
        for result in Result.objects.all():
            result.calculate_score()
