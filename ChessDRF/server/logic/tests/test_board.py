from django.test.testcases import TestCase
# from django.contrib.auth.models import User
from server.models import Figure, Game
from django.core.exceptions import ObjectDoesNotExist
from server.logic import Board
from .mixins import ChessCaseMixin


class TestBoard(TestCase, ChessCaseMixin):
    def setup_class(self):
        super().setup_class(self)
        self.game_0 = Game.objects.create(test=True, white_player=self.white_player, black_player=self.black_player)
        self.game_1 = Game.objects.create(test=True, white_player=self.white_player, black_player=self.black_player)
        self.board_0 = Board(self.game_0)
        self.board_1 = Board(self.game_1)
        self.board_0.initialize()
        self.board_1.initialize({
            (6, 0): {'is_white': True, 'role': 'king', 'status': 'N'}
        })
        self.king = Figure.objects.get(game=self.game_1, height=6, width=0)

    def test_default_dict(self):
        rook = Figure.objects.get(game=self.game_0, height=0, width=0)
        knight = Figure.objects.get(game=self.game_0, height=7, width=1)
        bishop = Figure.objects.get(game=self.game_0, height=0, width=5)
        pawn = Figure.objects.get(game=self.game_0, height=7, width=7)
        assert type(rook) == Figure
        assert knight.role == 'knight'
        assert bishop.is_white is True
        assert pawn.status == 'S'

    def test_custom_board(self):
        assert type(self.king) == Figure
        assert self.king.role == 'king'
        assert self.king.is_white is True
        assert self.king.status == 'N'
        assert self.king.height == 6
        assert self.king.width == 0

    def test_remove(self):
        rook_id = Figure.objects.get(game=self.game_0, height=0, width=0).id
        self.board_0.move_figure((0, 0), (0, 1))
        try:
            Figure.objects.get(game=self.game_0, height=0, width=0)
        except ObjectDoesNotExist:
            figure = Figure.objects.get(game=self.game_0, height=0, width=1)
            assert figure.id == rook_id
        else:
            assert False

    def test_move(self):
        pawn_id = Figure.objects.get(game=self.game_0, height=6, width=2).id
        self.board_0.move_figure((6, 2), (5, 2))
        try:
            Figure.objects.get(game=self.game_0, height=6, width=2)
        except ObjectDoesNotExist:
            figure = Figure.objects.get(game=self.game_0, height=5, width=2)
            assert figure.id == pawn_id
        else:
            assert False

    def test_get(self):
        rook = self.board_0.get(0, 0)
        none = self.board_0.get(3, 0)
        assert type(rook == Figure)
        assert none is None

    # def test_get_render_dict(self):
    #     product = self.board_0.get_render_dict()
    #     assert list(product) == []

