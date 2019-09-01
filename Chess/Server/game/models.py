from django.db import models
from django.contrib.auth.models import User


class Game(models.Model):
    white_player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='white')
    black_player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='black')


class Figure(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    is_white = models.BooleanField()
    role = models.CharField(max_length=8)
    status = models.CharField(max_length=8)
    height = models.SmallIntegerField()
    width = models.SmallIntegerField()
