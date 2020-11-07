# import pytest
from ChessDRF.logic import Board, Figure


class TestBoard:
    board_0 = Board()
    board_1 = Board({'white_turn': True, 'figures': {
        (6, 0): {'is_white': True, 'kind': 'king', 'status': 'N'}
    }})
    test_king = board_1.get((6, 0))

    def test_default_dict(self):
        assert type(self.board_0.get((0, 0))) == Figure
        assert self.board_0.get((7, 1)).kind == 'knight'
        assert self.board_0.get((1, 6)).is_white is True
        assert self.board_0.get((7, 7)).status == 'S'
        assert self.board_0.get((0, 4)).pos == (0, 4)
        assert self.board_0.get((6, 2)).symbol == 'P'

    def test_custom_board(self):
        assert type(self.test_king) == Figure
        assert self.test_king.kind == 'king'
        assert self.test_king.is_white is True
        assert self.test_king.status == 'N'
        assert self.test_king.pos == (6, 0)
        assert self.test_king.symbol == '@'

    def test_remove(self):
        assert self.board_0.get((0, 0)).kind == 'rook'
        assert self.board_0.get((0, 1)).kind == 'knight'
        self.board_0.move_figure((0, 0), (0, 1))
        assert self.board_0.get((0, 0)) is None
        assert self.board_0.get((0, 1)).kind == 'rook'

    def test_move(self):
        assert self.board_0.get((6, 2)).kind == 'pawn'
        assert self.board_0.get((5, 2)) is None
        self.board_0.move_figure((6, 2), (5, 2))
        assert self.board_0.get((6, 2)) is None
        assert self.board_0.get((5, 2)).kind == 'pawn'
