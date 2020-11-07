import pytest
from django.test.testcases import TestCase
from server.models import Figure, Game
from server.logic import Checker
from .mixins import ChessCaseMixin
from ...logic.manipulator import GameManipulator


class TestManipulator(TestCase, ChessCaseMixin):
    def setup_class(self):
        super().setup_class(self)
        self.manipulator = GameManipulator()

    @pytest.mark.run(order=14)
    def test_create(self):
        game = self.manipulator.create(self.white_player, True, self.black_player)
        assert game.black_player == self.black_player
        assert game.white_player == self.white_player
        assert game.status == 'I'
        assert not game.test
        assert game.white_message == 'Waiting for test_black...'
        assert game.black_message == 'Accept or decline test_white`s invite.'

    @pytest.mark.run(order=5)
    def test_create_existed(self):
        self.manipulator.create(self.black_player, True, self.white_player)
        try:
            self.manipulator.create(self.black_player, True, self.white_player)
        except ValueError:
            pass
        else:
            assert False, 'game already exists'

    @pytest.mark.run(order=6)
    def test_accept(self):
        game = self.manipulator.create(self.white_player, True, self.black_player)
        self.manipulator.accept(self.black_player, game)
        assert game.status == 'S'
        assert game.black_player == self.black_player
        assert game.white_player == self.white_player
        assert not game.test
        assert game.white_message == 'Your turn.'
        assert game.black_message == 'test_white turn. Please wait.'
        assert game.board.get_dict().get((0, 0)) == {'is_white': True, 'role': 'rook', 'status': 'S'}

    @pytest.mark.run(order=7)
    def test_decline(self):
        game = self.manipulator.create(self.white_player, True, self.black_player)
        self.manipulator.decline(self.black_player, game)
        assert game.status == 'R'
        assert game.black_player == self.black_player
        assert game.white_player == self.white_player
        assert not game.test
        assert game.board.get_dict().get((0, 0)) is None

    @pytest.mark.run(order=8)
    def test_turn(self):
        game = self.manipulator.create(self.white_player, True, self.black_player)
        self.manipulator.accept(self.black_player, game)
        status = self.manipulator.turn(self.white_player, game, (1, 1), (3, 1))
        assert status is None
        assert not game.white_turn
        assert game.white_message == 'Waiting for test_black...'
        assert game.black_message == 'Your turn.'

    @pytest.mark.run(order=9)
    def test_INF_turn(self):
        game = self.manipulator.create(self.white_player, True, self.black_player)
        self.manipulator.accept(self.black_player, game)
        status = self.manipulator.turn(self.white_player, game, (3, 1), (4, 4))
        assert status == 'INF'
        assert game.white_message == 'There is no figure!'

    @pytest.mark.run(order=10)
    def test_IFF_turn(self):
        game = self.manipulator.create(self.white_player, True, self.black_player)
        self.manipulator.accept(self.black_player, game)
        status = self.manipulator.turn(self.white_player, game, (6, 1), (4, 4))
        assert status == 'IFF'
        assert game.white_message == 'This figure is`nt yours!'

    @pytest.mark.run(order=11)
    def test_IM_turn(self):
        game = self.manipulator.create(self.white_player, True, self.black_player)
        self.manipulator.accept(self.black_player, game)
        status = self.manipulator.turn(self.white_player, game, (0, 0), (2, 2))
        assert status == 'IM'
        assert game.white_message == 'Illegal move!'

    @pytest.mark.run(order=12)
    def test_IC_turn(self):
        game = self.manipulator.create(self.white_player, True, self.black_player)
        self.manipulator.accept(self.black_player, game)
        game.board.move_figure((0, 4), (5, 4))
        king = game.board.get(5, 4)
        king.status = 'N'
        king.save()
        status = self.manipulator.turn(self.white_player, game, (5, 4), (5, 5))
        assert status == 'IC'
        assert game.white_message == 'Check your king!'

    @pytest.mark.run(order=13)
    def test_T_turn(self):
        game = self.manipulator.create(self.white_player, True, self.black_player)
        self.manipulator.accept(self.black_player, game)
        game.board.move_figure((1, 7), (6, 7))
        pawn = game.board.get(6, 7)
        pawn.status = 'N'
        pawn.save()
        status = self.manipulator.turn(self.white_player, game, (6, 7), (7, 6))
        assert status == 'T'
        assert game.has_transformation
        assert game.white_message == 'Select figure role to transform.'

    @pytest.mark.run(order=1)
    def test_check_end_of_game_mate(self):
        game = self.manipulator.create(self.white_player, True, self.black_player)
        self.manipulator.accept(self.black_player, game)
        game.board.initialize({
            (0, 0): {'is_white': True, 'role': 'king', 'status': 'S'},
            (0, 2): {'is_white': False, 'role': 'rook', 'status': 'S'},
            (2, 0): {'is_white': False, 'role': 'rook', 'status': 'S'},
            (2, 2): {'is_white': False, 'role': 'bishop', 'status': 'N'},
        })
        self.manipulator.check_end_of_game(game)
        assert game.status == 'B'
        assert game.white_player.games_played == game.black_player.games_played == 1
        assert game.white_player.games_lost == 1
        assert game.black_player.games_won == 1
        assert game.white_message == 'Sorry, you lose :( Lucky next time!'
        assert game.black_message == 'Congratulations! You win!'

    @pytest.mark.run(order=2)
    def test_check_end_of_game_stalemate(self):
        game = self.manipulator.create(self.white_player, True, self.black_player)
        self.manipulator.accept(self.black_player, game)
        game.board.initialize({
            (0, 0): {'is_white': True, 'role': 'king', 'status': 'S'},
            (1, 2): {'is_white': False, 'role': 'rook', 'status': 'S'},
            (2, 1): {'is_white': False, 'role': 'rook', 'status': 'S'},
        })
        self.manipulator.check_end_of_game(game)
        assert game.status == 'D'
        assert game.white_player.games_played == game.black_player.games_played == 2
        assert game.white_player.games_tied == game.black_player.games_tied == 1
        assert game.white_message == game.black_message == 'Draw. Reason: no possible moves.'

    @pytest.mark.run(order=3)
    def test_check_end_of_game_insufficient_mate(self):
        game = self.manipulator.create(self.white_player, True, self.black_player)
        self.manipulator.accept(self.black_player, game)
        game.board.initialize({
            (0, 0): {'is_white': True, 'role': 'king', 'status': 'S'},
            (1, 2): {'is_white': False, 'role': 'knight', 'status': 'S'},
        })
        self.manipulator.check_end_of_game(game)
        assert game.status == 'D'
        assert game.white_player.games_played == game.black_player.games_played == 3
        assert game.white_player.games_tied == game.black_player.games_tied == 2
        assert game.white_message == game.black_message == 'Draw. Reason: both players have insufficient pieces to win.'

    @pytest.mark.run(order=4)
    def test_check_end_of_game_false(self):
        game = self.manipulator.create(self.white_player, True, self.black_player)
        self.manipulator.accept(self.black_player, game)
        self.manipulator.check_end_of_game(game)
        assert game.status == 'S'
        assert game.white_player.games_played == game.black_player.games_played == 3
        assert game.white_player.games_tied == game.black_player.games_tied == 2
        assert game.white_player.games_lost == 1
        assert game.black_player.games_won == 1
        assert game.white_message == 'Your turn.'
        assert game.black_message == 'test_white turn. Please wait.'
