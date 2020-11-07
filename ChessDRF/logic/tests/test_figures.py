from itertools import product
import pytest
from ..figure import Figure


class TestCase:
    pass


class TestKing(TestCase):
    king = Figure(False, 'king', 'N', (1, 4))
    start_king = Figure(True, 'king', 'S', (0, 4))
    combo = product(range(3), range(3, 6))
    wrong_poses = {*product(range(8), range(8))} - set(combo)

    @pytest.mark.parametrize("height", range(3))
    @pytest.mark.parametrize("width", range(3, 6))
    def test_standard_move(self, height, width):
        pos = (height, width)
        if pos != (1, 4):
            assert self.king.move_check(pos) == 'MA', f'Problem pos: {pos}'

    def test_move_and_change_status(self):
        assert self.start_king.move_check((0, 3)) == 'MAS'

    def test_stay(self):
        assert self.king.move_check((1, 4)) == 'I'

    @pytest.mark.parametrize('params', ((3, 2, 0), (5, 6, 7)))
    def test_castling(self, params):
        first, last, rook = params
        assert self.start_king.move_check((0, last)) == f'QC [(0, {first}), (0, {last})] R (0, {rook})'

    @pytest.mark.parametrize('pos', wrong_poses)
    def test_wrong_moves(self, pos):
        assert self.king.move_check(pos) == 'I'


class TestRook(TestCase):
    rook = Figure(True, 'rook', 'N', (3, 4))
    start_rook = Figure(False, 'rook', 'S', (7, 7))
    combo_0 = {*product([3], range(8)), *product(range(8), [4])}
    combo_1 = {*product([7], range(8)), *product(range(8), [7])}
    wrong_poses = {*product(range(8), range(8))} - set(combo_0)

    @pytest.mark.parametrize('pos', combo_0)
    def test_move(self, pos):
        if pos != (3, 4):
            assert self.rook.move_check(pos) == f'QMA {self.rook.query(pos)}'

    @pytest.mark.parametrize('pos', combo_1)
    def test_move_and_check_status(self, pos):
        if pos != (7, 7):
            assert self.start_rook.move_check(pos) == f'QMAS {self.start_rook.query(pos)}'

    def test_stay(self):
        assert self.rook.move_check((3, 4)) == 'I'

    @pytest.mark.parametrize('pos', wrong_poses)
    def test_wrong_moves(self, pos):
        assert self.rook.move_check(pos) == 'I'


class TestBishop(TestCase):
    bishop = Figure(True, 'bishop', 'N', (6, 4))
    combo = {*[(i + 2, i) for i in range(6)], *[(i, 10 - i) for i in range(3, 8)]}
    wrong_poses = {*product(range(8), range(8))} - set(combo)

    @pytest.mark.parametrize("pos", combo)
    def test_move(self, pos):
        if pos != (6, 4):
            assert self.bishop.move_check(pos) == f'QMA {self.bishop.query(pos)}'

    def test_stay(self):
        assert self.bishop.move_check((6, 4)) == 'I'

    @pytest.mark.parametrize('pos', wrong_poses)
    def test_wrong_moves(self, pos):
        assert self.bishop.move_check(pos) == 'I'


class TestQueen(TestCase):
    queen = Figure(False, 'queen', 'N', (1, 5))
    combo_0 = *product([1], range(8)), *product(range(8), [5])
    combo_1 = *[(i, i + 4) for i in range(0, 4)], *[(i, 6 - i) for i in range(7)]
    combo = {*combo_0, *combo_1}
    wrong_poses = {*product(range(8), range(8))} - set(combo)

    @pytest.mark.parametrize("pos", combo)
    def test_move(self, pos):
        if pos != (1, 5):
            assert self.queen.move_check(pos) == f'QMA {self.queen.query(pos)}'

    def test_stay(self):
        assert self.queen.move_check((1, 5)) == 'I'

    @pytest.mark.parametrize('pos', wrong_poses)
    def test_wrong_moves(self, pos):
        assert self.queen.move_check(pos) == 'I'


class TestKnight(TestCase):
    knight = Figure(True, 'knight', 'N', (4, 4))
    combo = *product((1, -1), (2, -2)), *product((2, -2), (1, -1))
    combo = {(i[0] + 4, i[1] + 4) for i in combo}

    @pytest.mark.parametrize('pos', combo)
    def test_move(self, pos):
        assert self.knight.move_check(pos) == 'MA'

    def test_stay(self):
        assert self.knight.move_check((1, 1)) == 'I'


class TestPawn(TestCase):
    start_pawn = Figure(True, 'pawn', 'S', (1, 5))
    pawn = Figure(False, 'pawn', 'N', (2, 3))
    transforming_pawn = Figure(False, 'pawn', 'N', (1, 4))
    en_passant_pawn = Figure(True, 'pawn', 'N', (4, 2))

    def test_move_and_check_status(self):
        assert self.start_pawn.move_check((2, 5)) == 'MS'

    def test_move(self):
        assert self.pawn.move_check((1, 3)) == 'M'

    def test_transform(self):
        assert self.transforming_pawn.move_check((0, 4)) == 'MS'

    def test_en_passant(self):
        assert self.en_passant_pawn.move_check((5, 3)) == 'AE P (4, 3)'

    def test_two_steps(self):
        assert self.start_pawn.move_check((3, 5)) == 'QMS [(2, 5), (3, 5)]'

    @pytest.mark.parametrize('width', (2, 4))
    def test_attack(self, width):
        assert self.pawn.move_check((1, width)) == 'A'

    @pytest.mark.parametrize('width', (3, 5))
    def test_attack_transform(self, width):
        assert self.transforming_pawn.move_check((0, width)) == 'AS'

    @pytest.mark.parametrize('width', (4, 6))
    def test_attack_and_check_status(self, width):
        assert self.start_pawn.move_check((2, width)) == 'AS'
