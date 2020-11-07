from django.test.testcases import TestCase
from .mixins import ChessCaseMixin
from .. import Game, Figure
from ...logic import Board


class TestGame(TestCase, ChessCaseMixin):
    def setup_class(self):
        super().setup_class(self)
        self.start_dict = {
            (0, 0): {'is_white': True, 'role': 'rook', 'status': 'S'},
            (0, 1): {'is_white': True, 'role': 'knight', 'status': 'N'},
            (0, 4): {'is_white': True, 'role': 'king', 'status': 'S'},
            (0, 7): {'is_white': True, 'role': 'rook', 'status': 'S'},
            (1, 1): {'is_white': True, 'role': 'pawn', 'status': 'S'},
            (2, 2): {'is_white': False, 'role': 'knight', 'status': 'N'},
            (4, 2): {'is_white': True, 'role': 'pawn', 'status': 'N'},
            (4, 3): {'is_white': False, 'role': 'pawn', 'status': 'E'},
            (6, 0): {'is_white': False, 'role': 'pawn', 'status': 'S'},
            (6, 6): {'is_white': True, 'role': 'pawn', 'status': 'N'},
        }
        self.game = Game.objects.create(test=True, white_turn=True, white_player=self.white_player,
                                        black_player=self.black_player, status='S')
        self.game.board = self.board = Board(self.game)
        self.board.initialize(self.start_dict)

    def test_incorrect_create(self):
        try:
            Game.create(test=True, white_player=self.black_player, black_player=self.black_player, status='S')
        except ValueError:
            pass
        else:
            assert False

    def test_create_dummy(self):
        dummy = self.game.create_dummy()
        assert dummy.test
        assert dummy.white_player == self.game.white_player
        assert dummy.status == self.game.status
        assert dummy.board.get(2, 2).role == 'knight'

    def test__move_or_attack_0(self):
        rook_id = self.board.get(0, 0).id
        rook = Figure.objects.get(id=rook_id)
        self.game._move_or_attack((rook.height, rook.width), (1, 0))
        assert not self.board.get(0, 0)
        assert self.board.get(1, 0) == rook
        rook = Figure.objects.get(id=rook_id)
        self.game._move_or_attack((rook.height, rook.width), (3, 0))
        assert not self.board.get(1, 0)
        assert self.board.get(3, 0) == rook
        rook = Figure.objects.get(id=rook_id)
        self.game._move_or_attack((rook.height, rook.width), (6, 0))
        assert not self.board.get(3, 0)
        assert self.board.get(6, 0) == rook

    def test__move_or_attack_1(self):
        knight_id = self.board.get(0, 1).id
        knight = Figure.objects.get(id=knight_id)
        self.game._move_or_attack((knight.height, knight.width), (2, 2))
        assert not self.board.get(0, 1)
        assert self.board.get(2, 2) == knight
        knight = Figure.objects.get(id=knight_id)
        self.game._move_or_attack((knight.height, knight.width), (4, 1))
        assert not self.board.get(2, 2)
        assert self.board.get(4, 1) == knight

    def test__castling(self):
        king = self.board.get(0, 4)
        rook = self.board.get(0, 7)
        self.game._castling((0, 4), (0, 6), 'QC [(0, 5), (0, 6)] R (0, 7)')
        assert not self.board.get(0, 4)
        assert not self.board.get(0, 7)
        assert self.board.get(0, 6) == king
        assert self.board.get(0, 5) == rook

    def test__en_passant(self):
        pawn_id = self.board.get(4, 2).id
        self.game._en_passant((4, 2), (5, 3), 'AE P (4, 3)')
        assert not self.board.get(4, 3)
        assert not self.board.get(4, 2)
        assert self.board.get(5, 3).id == pawn_id

    def test_renew(self):
        pawn_id = self.board.get(1, 1).id
        pawn = Figure.objects.get(id=pawn_id)
        self.game.turn((pawn.height, pawn.width), (3, 1))
        assert not self.game.white_turn
        pawn = Figure.objects.get(id=pawn_id)
        assert pawn.status == 'E'
        self.game.renew()
        pawn = Figure.objects.get(id=pawn_id)
        assert self.game.white_turn
        assert pawn.status == 'N'

    def test_act(self):
        self.game.board.initialize(self.start_dict)
        rook_id = self.board.get(0, 0).id
        rook = Figure.objects.get(id=rook_id)
        self.game.act((0, 0), (1, 0), 'MS')
        assert not self.board.get(0, 0)
        assert self.board.get(1, 0) == rook
        rook = Figure.objects.get(id=rook_id)
        self.game._move_or_attack((rook.height, rook.width), (3, 0))
        assert not self.board.get(1, 0)
        assert self.board.get(3, 0) == rook
        rook = Figure.objects.get(id=rook_id)
        self.game._move_or_attack((rook.height, rook.width), (6, 0))
        assert not self.board.get(3, 0)
        assert self.board.get(6, 0) == rook

    def test_transformation(self):
        self.game.test = False
        self.game.save()
        pawn_id = self.board.get(6, 6).id
        pawn = Figure.objects.get(id=pawn_id)
        status = self.game.turn((pawn.height, pawn.width), (7, 6))
        assert status == 'T'
        assert self.game.has_transformation
        self.game.turn(None, None, 'knight')
        pawn = Figure.objects.get(id=pawn_id)
        assert pawn.status == 'N'
        assert pawn.role == 'knight'
        self.game.test = True
        self.game.save()
