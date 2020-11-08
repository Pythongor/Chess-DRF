from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver


class ChessUser(AbstractUser):
    """class for representing player profile"""
    games_played = models.PositiveSmallIntegerField(default=0)
    games_won = models.PositiveSmallIntegerField(default=0)
    games_tied = models.PositiveSmallIntegerField(default=0)
    games_lost = models.PositiveSmallIntegerField(default=0)
    photo = models.ImageField(upload_to="photo/")
    is_online = models.BooleanField(default=False)


@receiver(user_logged_in)
def got_online(sender, user, request, **kwargs):
    user.is_online = True
    user.save()


@receiver(user_logged_out)
def got_offline(sender, user, request, **kwargs):
    user.is_online = False
    user.save()
