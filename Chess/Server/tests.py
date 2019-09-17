from django.test import TestCase
from django.contrib.auth.models import User

from .models import Game, Figure
from .game_checker import GameChecker
from .game_manipulator import GameManipulator


class TestFigure(TestCase):
    def setUp(self):
        self.white_player = User.objects.create_user(username='White',
                                                     password='white')
        self.black_player = User.objects.create_user(username='Black',
                                                     password='black')
        self.game = Game.objects.create(white_player=self.white_player,
                                        black_player=self.black_player)
        self.white_pawn = Figure(game=self.game, owner=self.white_player, role='pawn',
                                 is_white=True, height=2, width=5, status='START')
        self.black_pawn = Figure(game=self.game, owner=self.black_player, role='pawn',
                                 is_white=False, height=4, width=7, status='NORMAL')
        self.white_king = Figure(game=self.game, owner=self.white_player, role='king',
                                 is_white=True, height=1, width=5, status='START')

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

    def test_king_move_possibility(self):
        simple_move = self.white_king.move_possibility([2, 5])
        simple_possible = {'CHECKUP': 'MOVE ATTACK STATUS', 'COORDINATES': [2, 5]}
        castling_move = self.white_king.move_possibility([1, 7])
        castling_possible = {'CHECKUP': 'MOVE CASTLING',
                             'QUERY': [[1, 5], [1, 6], [1, 7]]}
        self.assertEqual(simple_move, simple_possible)
        self.assertEqual(castling_move, castling_possible)


class TestGameChecker(TestCase):
    def setUp(self):
        self.white_player = User.objects.create_user(username='White',
                                                     password='white')
        self.black_player = User.objects.create_user(username='Black',
                                                     password='black')
        self.game = Game.objects.create(white_player=self.white_player,
                                        black_player=self.black_player)
        self.checker = GameChecker(self.game)
        self.manipulator = GameManipulator(self.game)
        self.white_pawn = Figure.objects.create(
            game=self.game, owner=self.white_player, role='pawn', is_white=True,
            height=2, width=5, status='START')
        self.black_pawn = Figure.objects.create(
            game=self.game, owner=self.black_player, role='pawn', is_white=False,
            height=4, width=7, status='NORMAL')
        self.pawn_to_transform = Figure.objects.create(
            game=self.game, height=2, owner=self.black_player, role='pawn',
            is_white=False, width=1, status='NORMAL')
        self.dummy_0 = Figure.objects.create(
            game=self.game, owner=self.white_player, role='pawn', is_white=True,
            height=3, width=8, status='START')
        self.dummy_1 = Figure.objects.create(
            game=self.game, owner=self.white_player, role='pawn', is_white=True,
            height=4, width=6, status='EN PASSANT')
        self.white_king = Figure.objects.create(
            game=self.game, owner=self.white_player, role='king', is_white=True,
            height=1, width=5, status='START')
        self.white_rook = Figure.objects.create(
            game=self.game, owner=self.white_player, role='rook', is_white=True,
            height=1, width=8, status='START')

    def test_get_figure(self):
        white_left_rook = self.checker.get_figure([1, 8])
        self.assertEqual(white_left_rook.game, self.game)
        self.assertEqual(white_left_rook.owner.username, 'White')
        self.assertEqual(white_left_rook.is_white, True)
        self.assertEqual(white_left_rook.role, 'rook')
        self.assertEqual(white_left_rook.status, 'START')
        self.assertEqual(white_left_rook.height, 1)
        self.assertEqual(white_left_rook.width, 8)

    def test_en_passant(self):
        self.manipulator.start(False)
        self.manipulator._switch_players()
        # check = self.checker._en_passant_checkup([4, 7], [3, 6])

        check = self.checker.create_command([[4, 7], [3, 6]])

        # check = self.checker._en_passant_checkup([4, 7], [3, 6])
        output = {'ACCEPT EN PASSANT': [[4, 7], [4, 6], [3, 6]]}
        self.assertEqual(check, output)

    def test_castling(self):
        self.manipulator.start(False)
        check = self.checker.create_command([[1, 5], [1, 7]])
        output = {'CASTLING ACCEPT': [[1, 5], '1']}
        self.assertEqual(check, output)


class TestGameManipulator(TestCase):
    def setUp(self):
        self.white_player = User.objects.create_user(username='White',
                                                     password='white')
        self.black_player = User.objects.create_user(username='Black',
                                                     password='black')
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

    def test_switch_players(self):
        self.manipulator.start()
        self.manipulator._switch_players()
        self.assertEqual(self.game.black_message, 'Your turn')
        self.assertEqual(self.game.white_message, 'Wait your turn')
        self.assertEqual(self.game.white_turn, False)

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


class TestFigureManipulation(TestCase):
    def setUp(self):
        self.white_player = User.objects.create_user(username='White',
                                                     password='white')
        self.black_player = User.objects.create_user(username='Black',
                                                     password='black')
        self.game = Game.objects.create(white_player=self.white_player,
                                        black_player=self.black_player)
        self.checker = GameChecker(self.game)
        self.manipulator = GameManipulator(self.game)
        self.white_pawn = Figure.objects.create(
            game=self.game, owner=self.white_player, role='pawn', is_white=True,
            height=2, width=5, status='START')
        self.black_pawn = Figure.objects.create(
            game=self.game, owner=self.black_player, role='pawn', is_white=False,
            height=4, width=7, status='NORMAL')
        self.pawn_to_transform = Figure.objects.create(
            game=self.game, height=2, owner=self.black_player, role='pawn',
            is_white=False, width=1,  status='NORMAL')
        self.dummy_0 = Figure.objects.create(
            game=self.game, owner=self.white_player,  role='pawn', is_white=True,
            height=3, width=8, status='START')
        self.dummy_1 = Figure.objects.create(
            game=self.game, owner=self.white_player, role='pawn', is_white=True,
            height=4, width=6, status='EN PASSANT')
        self.white_king = Figure.objects.create(
            game=self.game, owner=self.white_player, role='king', is_white=True,
            height=1, width=5, status='START')
        self.white_rook = Figure.objects.create(
            game=self.game, owner=self.white_player, role='rook', is_white=True,
            height=1, width=8, status='START')

    def test_pawn_move(self):
        pawn_0 = self.checker.get_figure([2, 5])
        command = {'MOVE ACCEPT': [[2, 5], [3, 5]]}
        self.manipulator.make_move(command)
        pawn_1 = self.checker.get_figure([3, 5])
        self.assertEqual(pawn_0, pawn_1)

    def test_pawn_attack(self):
        pawn_0 = self.checker.get_figure([4, 7])
        command = {'ATTACK ACCEPT': [[4, 7], [3, 8]]}
        self.manipulator.make_move(command)
        pawn_1 = self.checker.get_figure([3, 8])
        self.assertEqual(pawn_0, pawn_1)

    def test_en_passant(self):
        pawn_0 = self.checker.get_figure([4, 7])
        command = {'ACCEPT EN PASSANT': [[4, 7], [4, 6], [3, 6]]}
        self.manipulator.make_move(command)
        pawn_1 = self.checker.get_figure([3, 6])
        dummy = self.checker.get_figure([4, 6])
        self.assertIsNone(dummy)
        self.assertEqual(pawn_0, pawn_1)

    def test_transformation(self):
        pawn = self.checker.get_figure([2, 1])
        command = {'MOVE TRANSFORMATION': [[2, 1], [1, 1]]}
        self.manipulator.make_move(command)
        queen = self.checker.get_figure([1, 1])
        self.assertEqual(pawn, queen)
        self.assertEqual(queen.role, 'queen')

    def test_castling(self):
        king_0 = self.checker.get_figure([1, 5])
        rook_0 = self.checker.get_figure([1, 8])
        command = {'CASTLING ACCEPT': [[[1, 5], [1, 7]], '1']}
        self.manipulator.make_move(command)
        king_1 = self.checker.get_figure([1, 7])
        rook_1 = self.checker.get_figure([1, 6])
        self.assertEqual(king_0, king_1)
        self.assertEqual(rook_0, rook_1)
