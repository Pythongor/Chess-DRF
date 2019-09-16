from django.test import TestCase
from django.contrib.auth.models import User

from .models import Game, Figure
from .game_checker import GameChecker
from .game_manipulator import GameManipulator


class TestFigure(TestCase):
    def setUp(self):
        self.white_player = User.objects.create_user(username='White', password='white')
        self.black_player = User.objects.create_user(username='Black', password='black')
        self.game = Game.objects.create(white_player=self.white_player,
                                        black_player=self.black_player)
        self.white_pawn = Figure(game=self.game, owner=self.white_player, role='pawn',
                                 is_white=True, height=2, width=5, status='STARTED')
        self.black_pawn = Figure(game=self.game, owner=self.black_player, role='pawn',
                                 is_white=False, height=4, width=7, status='NORMAL')
        self.dummy_0 = Figure(game=self.game, owner=self.white_player, role='pawn',
                              is_white=True, height=3, width=8, status='STARTED')
        self.dummy_1 = Figure(game=self.game, owner=self.white_player, role='pawn',
                              is_white=True, height=4, width=6, status='EN PASSANT')
        self.white_king = Figure(game=self.game, owner=self.white_player, role='pawn',
                                 is_white=True, height=2, width=5, status='STARTED')

    def test_pawn_move_possibility(self):
        simple_move = self.white_pawn.move_possibility([3, 5])
        simple_possible = {'CHECKUP': 'MOVE', 'COORDINATES': [3, 5]}
        en_passant_move = self.white_pawn.move_possibility([4, 5])
        en_passant_possible = {'CHECKUP': 'MOVE', 'QUERY': [[3, 5], [4, 5]]}
        self.assertEqual(simple_move, simple_possible)
        self.assertEqual(en_passant_move, en_passant_possible)

    def test_pawn_attack_possibility(self):
        simple_attack = self.black_pawn.move_possibility([3, 8])
        simple_possible = {'CHECKUP': 'ATTACK', 'COORDINATES': [3, 8]}
        en_passant_attack = self.black_pawn.move_possibility([3, 6])
        en_passant_possible = {'CHECKUP': 'ATTACK', 'COORDINATES': [3, 6]}
        self.assertEqual(simple_attack, simple_possible)
        self.assertEqual(en_passant_attack, en_passant_possible)


class TestGameChecker(TestCase):
    def setUp(self):
        self.white_player = User.objects.create_user(username='White', password='white')
        self.black_player = User.objects.create_user(username='Black', password='black')
        self.game = Game.objects.create(white_player=self.white_player,
                                        black_player=self.black_player)
        self.checker = GameChecker(self.game)
        self.manipulator = GameManipulator(self.game)

    def test_get_figure(self):
        self.manipulator.start()
        white_left_knight = self.checker.get_figure([1, 2])
        self.assertEqual(white_left_knight.game, self.game)
        self.assertEqual(white_left_knight.owner.username, 'White')
        self.assertEqual(white_left_knight.is_white, True)
        self.assertEqual(white_left_knight.role, 'knight')
        self.assertEqual(white_left_knight.status, 'NORMAL')
        self.assertEqual(white_left_knight.height, 1)
        self.assertEqual(white_left_knight.width, 2)


class TestGameManipulator(TestCase):
    def setUp(self):
        self.white_player = User.objects.create_user(username='White', password='white')
        self.black_player = User.objects.create_user(username='Black', password='black')
        self.game = Game.objects.create(white_player=self.white_player,
                                        black_player=self.black_player)
        self.checker = GameChecker(self.game)
        self.manipulator = GameManipulator(self.game)

    def test_start(self):
        self.assertEqual(self.game.status, 'INVITED')
        self.assertIsNone(self.game.white_turn)
        self.assertIsNone(self.game.white_message)
        self.assertIsNone(self.game.black_message)
        self.manipulator.start()
        self.assertEqual(self.game.status, 'STARTED')
        self.assertEqual(self.game.white_turn, True)
        self.assertEqual(self.game.white_message, 'Your turn')
        self.assertEqual(self.game.black_message, 'Wait your turn')

    def test_create_figures(self):
        self.manipulator.start()
        for index, role in enumerate(['rook', 'knight', 'bishop', 'queen',
                                      'king', 'bishop', 'knight', 'rook']):
            status = 'START' if role in ('rook', 'king') else 'NORMAL'
            white_figure = self.checker.get_figure([1, index + 1])
            white_pawn = self.checker.get_figure([2, index + 1])
            black_figure = self.checker.get_figure([8, index + 1])
            black_pawn = self.checker.get_figure([7, index + 1])
            parameters = (
                (white_figure.game, self.game), (white_figure.owner.username, 'White'),
                (white_figure.is_white, True), (white_figure.role, role),
                (white_figure.status, status), (white_figure.height, 1),
                (white_figure.width, index + 1), (black_figure.game, self.game),
                (black_figure.owner.username, 'Black'), (black_figure.is_white, False),
                (black_figure.role, role), (black_figure.status, status),
                (black_figure.height, 8), (black_figure.width, index + 1),
                (white_pawn.game, self.game), (white_pawn.owner.username, 'White'),
                (white_pawn.is_white, True), (white_pawn.role, 'pawn'),
                (white_pawn.status, 'NORMAL'), (white_pawn.height, 2),
                (white_pawn.width, index + 1), (black_pawn.game, self.game),
                (black_pawn.owner.username, 'Black'), (black_pawn.is_white, False),
                (black_pawn.role, 'pawn'), (black_pawn.status, 'NORMAL'),
                (black_pawn.height, 7), (black_pawn.width, index + 1),
            )
            for i, j in parameters:
                self.assertEqual(i, j)
