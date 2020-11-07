from django.db import models
from django.contrib.auth.models import AbstractUser


class ChessUser(AbstractUser):
    """class for representing player profile"""
    games_played = models.PositiveSmallIntegerField(default=0)
    games_won = models.PositiveSmallIntegerField(default=0)
    games_tied = models.PositiveSmallIntegerField(default=0)
    games_lost = models.PositiveSmallIntegerField(default=0)
    photo = models.ImageField(upload_to="photo/")


# @receiver(post_save, sender=User)
# def update_profile_signal(sender, instance, created, **kwargs):
#     if created:
#         figure = choice(listdir(f'{settings.STATIC_ROOT}/figures'))
#         photo = f'/figures/{figure}'
#         Profile.objects.create(user=instance, photo=photo)
#     instance.profile.save()
