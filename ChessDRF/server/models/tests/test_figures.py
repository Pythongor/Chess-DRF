from itertools import product
from django.test.testcases import TestCase
from server.models import Figure, Game
from .mixins import ChessCaseMixin


class TestKing(TestCase, ChessCaseMixin):
    combo = product(range(3), range(3, 6))
    wrong_poses = {*product(range(8), range(8))} - set(combo)

    def setup_class(self):
        super().setup_class(self)
        self.game = Game.objects.create(status='S', white_player=self.white_player, black_player=self.black_player)
        self.king = Figure.objects.create(is_white=False, role='king', status='N',
                                          height=1, width=4, game=self.game)
        self.start_king = Figure.objects.create(is_white=True, role='king', status='S',
                                                height=0, width=4, game=self.game)

    def test_standard_move(self):
        for pos in self.combo:
            if pos != (1, 4):
                assert self.king.move_check(*pos) == 'MA', f'{pos}'

    def test_move_and_change_status(self):
        assert self.start_king.move_check(0, 3) == 'MAS'

    def test_stay(self):
        assert self.king.move_check(1, 4) == 'I'

    def test_castling(self):
        for params in ((3, 2, 0), (5, 6, 7)):
            first, last, rook = params
            assert self.start_king.move_check(0, last) == f'QC [(0, {first}), (0, {last})] R (0, {rook})'

    def test_wrong_moves(self):
        for pos in self.wrong_poses:
            assert self.king.move_check(*pos) == 'I'


class TestRook(TestCase, ChessCaseMixin):
    combo_0 = {*product([3], range(8)), *product(range(8), [4])}
    combo_1 = {*product([7], range(8)), *product(range(8), [7])}
    wrong_poses = {*product(range(8), range(8))} - set(combo_0)

    def setup_class(self):
        super().setup_class(self)
        self.game = Game.objects.create(status='S', white_player=self.white_player, black_player=self.black_player)
        self.rook = Figure(is_white=True, role='rook', status='N', height=3, width=4, game=self.game)
        self.start_rook = Figure(is_white=False, role='rook', status='S', height=7, width=7, game=self.game)

    def test_move(self):
        for pos in self.combo_0:
            if pos != (3, 4):
                assert self.rook.move_check(*pos) == f'QMA {self.rook.query(*pos)}'

    def test_move_and_check_status(self):
        for pos in self.combo_1:
            if pos != (7, 7):
                assert self.start_rook.move_check(*pos) == f'QMAS {self.start_rook.query(*pos)}'

    def test_stay(self):
        assert self.rook.move_check(3, 4) == 'I'

    def test_wrong_moves(self):
        for pos in self.wrong_poses:
            assert self.rook.move_check(*pos) == 'I'


class TestBishop(TestCase, ChessCaseMixin):
    combo = {*[(i + 2, i) for i in range(6)], *[(i, 10 - i) for i in range(3, 8)]}
    wrong_poses = {*product(range(8), range(8))} - set(combo)

    def setup_class(self):
        super().setup_class(self)
        self.game = Game.objects.create(status='S', white_player=self.white_player, black_player=self.black_player)
        self.bishop = Figure(is_white=True, role='bishop', status='N', height=6, width=4, game=self.game)

    def test_move(self):
        for pos in self.combo:
            if pos != (6, 4):
                assert self.bishop.move_check(*pos) == f'QMA {self.bishop.query(*pos)}'

    def test_stay(self):
        assert self.bishop.move_check(6, 4) == 'I'

    def test_wrong_moves(self):
        for pos in self.wrong_poses:
            assert self.bishop.move_check(*pos) == 'I'


class TestQueen(TestCase, ChessCaseMixin):
    combo_0 = *product([1], range(8)), *product(range(8), [5])
    combo_1 = *[(i, i + 4) for i in range(0, 4)], *[(i, 6 - i) for i in range(7)]
    combo = {*combo_0, *combo_1}
    wrong_poses = {*product(range(8), range(8))} - set(combo)

    def setup_class(self):
        super().setup_class(self)
        self.game = Game.objects.create(status='S', white_player=self.white_player, black_player=self.black_player)
        self.queen = Figure(is_white=False, role='queen', status='N', height=1, width=5, game=self.game)

    def test_move(self):
        for pos in self.combo:
            if pos != (1, 5):
                assert self.queen.move_check(*pos) == f'QMA {self.queen.query(*pos)}'

    def test_stay(self):
        assert self.queen.move_check(1, 5) == 'I'

    def test_wrong_moves(self):
        for pos in self.wrong_poses:
            assert self.queen.move_check(*pos) == 'I'


class TestKnight(TestCase, ChessCaseMixin):
    combo = *product((1, -1), (2, -2)), *product((2, -2), (1, -1))
    combo = {(i[0] + 4, i[1] + 4) for i in combo}
    wrong_poses = {*product(range(8), range(8))} - set(combo)

    def setup_class(self):
        super().setup_class(self)
        self.game = Game.objects.create(status='S', white_player=self.white_player, black_player=self.black_player)
        self.knight = Figure(is_white=True, role='knight', status='N', height=4, width=4, game=self.game)

    def test_move(self):
        for pos in self.combo:
            assert self.knight.move_check(*pos) == 'MA'

    def test_stay(self):
        assert self.knight.move_check(1, 1) == 'I'

    def test_wrong_moves(self):
        for pos in self.wrong_poses:
            assert self.knight.move_check(*pos) == 'I'


class TestPawn(TestCase, ChessCaseMixin):
    def setup_class(self):
        super().setup_class(self)
        self.game = Game.objects.create(status='S', white_player=self.white_player, black_player=self.black_player)
        self.start_pawn = Figure(is_white=True, role='pawn', status='S', height=1, width=5, game=self.game)
        self.pawn = Figure(is_white=False, role='pawn', status='N', height=2, width=3, game=self.game)
        self.transforming_pawn = Figure(is_white=False, role='pawn', status='N', height=1, width=4, game=self.game)
        self.en_passant_pawn = Figure(is_white=True, role='pawn', status='N', height=4, width=2, game=self.game)

    def test_move_and_check_status(self):
        assert self.start_pawn.move_check(2, 5) == 'MS'

    def test_move(self):
        assert self.pawn.move_check(1, 3) == 'M'

    def test_transform(self):
        assert self.transforming_pawn.move_check(0, 4) == 'MS'

    def test_en_passant(self):
        assert self.en_passant_pawn.move_check(5, 3) == 'AE P (4, 3), (5, 3)'

    def test_two_steps(self):
        assert self.start_pawn.move_check(3, 5) == 'QMS [(2, 5), (3, 5)]'

    def test_attack(self):
        for width in (2, 4):
            assert self.pawn.move_check(1, width) == 'A'

    def test_attack_transform(self):
        for width in (3, 5):
            assert self.transforming_pawn.move_check(0, width) == 'AS'

    def test_attack_and_check_status(self):
        for width in (4, 6):
            assert self.start_pawn.move_check(2, width) == 'AS'
