from django.test import TestCase
from django.contrib.auth.models import User

from ..game_checker import GameChecker
from ..models import Game, Figure


class TestGameChecker(TestCase):
    def setUp(self):
        white_player = User(username='White', password='white')
        black_player = User(username='Black', password='black')
        game = Game(white_player=white_player, black_player=black_player)
