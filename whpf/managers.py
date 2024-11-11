from django.db import models


class PlayerManager(models.Manager):
    def get_queryset(self):
        return super(PlayerManager, self).get_queryset().filter(active=True, faceless=False)
