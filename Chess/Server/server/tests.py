
from django.test import TestCase
from django.contrib.auth.models import User

from .game_checker import GameChecker
from .models import Game, Figure


class TestGameChecker(TestCase):
    def setUp(self):
        self.white_player = User(username='White', password='white')
        self.black_player = User(username='Black', password='black')
        # game = Game(white_player=self.white_player, black_player=self.black_player)

    def test_users(self):
        self.assertEqual(self.white_player.username, 'White')