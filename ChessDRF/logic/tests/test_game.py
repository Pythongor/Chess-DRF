from ChessDRF.logic import (Game, Board, Checker,
                            # Controller
                            )


class TestChecker:
    game = Game(True)
    checker = game.checker
    game_1 = Game(True)
    checker_1 = game_1.checker
    game_1.board = checker_1.board = Board({'white_turn': True, 'figures': {
        (0, 0): {'is_white': True, 'kind': 'king', 'status': 'S'},
        (0, 2): {'is_white': False, 'kind': 'rook', 'status': 'S'},
        (2, 0): {'is_white': False, 'kind': 'rook', 'status': 'S'},
        (2, 2): {'is_white': False, 'kind': 'bishop', 'status': 'N'},
    }})
    game_2 = Game(True)
    checker_2 = game_2.checker
    game_2.board = checker_2.board = Board({'white_turn': True, 'figures': {
        (0, 0): {'is_white': True, 'kind': 'king', 'status': 'S'},
        (1, 2): {'is_white': False, 'kind': 'rook', 'status': 'S'},
        (2, 1): {'is_white': False, 'kind': 'rook', 'status': 'S'},
    }})

    def test__get_query(self):
        query = '[(2, 2), (4, 6)]'
        assert Checker._get_query(query) == [(2, 2), (4, 6)]

    def test__check_correct_figure_select(self):
        figure = self.game.board.get((0, 1))
        none = self.game.board.get((4, 1))
        enemy = self.game.board.get((7, 1))
        assert self.checker._check_correct_figure_select(figure, (2, 2)) == 'MA'
        assert self.checker._check_correct_figure_select(none, (2, 2)) is None
        assert self.checker._check_correct_figure_select(enemy, (5, 2)) is None

    def test__check_move(self):
        assert self.checker._check_move((5, 5), '')
        assert not self.checker._check_move((0, 5), '')
        assert not self.checker._check_move((7, 5), '')

    def test__check_attack(self):
        assert not self.checker._check_attack((5, 5), '')
        assert not self.checker._check_attack((0, 5), '')
        assert self.checker._check_attack((7, 5), '')

    def test__check_move_and_attack(self):
        assert self.checker._check_move_and_attack((5, 5), '')
        assert not self.checker._check_move_and_attack((0, 5), '')
        assert self.checker._check_move_and_attack((7, 5), '')

    def test__check_move_query(self):
        assert not self.checker._check_move_query((2, 7), 'QM [(1, 6), (2, 7)]')
        assert not self.checker._check_move_query((5, 6), 'QM [(6, 6), (5, 7)]')
        assert self.checker._check_move_query((4, 0), 'QM [(4, 6), (4, 5), (4, 4), (4, 3), (4, 2), (4, 1), (4, 0)]')
        assert not self.checker._check_move_query((4, 0), 'QM [(2, 4), (3, 4), (4, 4), (5, 4), (6, 4)]')

    def test__check_move_and_attack_query(self):
        assert not self.checker._check_move_and_attack_query((2, 7), 'QM [(1, 6), (2, 7)]')
        assert not self.checker._check_move_and_attack_query((5, 6), 'QM [(6, 6), (5, 7)]')
        assert self.checker._check_move_and_attack_query((4, 0),
                                                         'QM [(4, 6), (4, 5), (4, 4), (4, 3), (4, 2), (4, 1), (4, 0)]')
        assert self.checker._check_move_and_attack_query((4, 0), 'QM [(2, 4), (3, 4), (4, 4), (5, 4), (6, 4)]')

    def test__check_castling(self):
        for i in (1, 2, 3, 5, 6):
            del self.game.board[(0, i)]
        for i in range(8):
            del self.game.board[(1, i)]
        del self.game.board[(6, 3)]
        assert self.checker._check_castling((0, 6), 'QC [(0, 5), (0, 6)] R (0, 7)')
        assert not self.checker._check_castling((0, 6), 'QC [(0, 3), (0, 2)] R (0, 0)')

    def test_is_tile_under_attack(self):
        assert not self.checker.is_tile_under_attack((0, 0))
        assert self.checker.is_tile_under_attack((5, 0))

    def test__is_act_danger_for_king(self):
        king = self.checker.board[(0, 4)]
        assert self.checker._is_act_danger_for_king(king, (0, 3), 'M')

    def test__check_en_passant(self):
        self.game.board.move_figure((6, 0), (4, 0))
        self.game.board[(4, 0)].status = 'E'
        assert self.checker._check_en_passant((3, 0), 'AE P (4, 0)')

    def test_check_mate(self):
        assert self.checker_1.check_end_of_game() == 'M'
        self.game_1.board.move_figure((0, 2), (0, 1))
        assert not self.checker_1.check_end_of_game()

    def test_check_stalemate(self):
        assert self.checker_2.check_end_of_game() == 'SM'

    def test_check_insufficient(self):
        del self.checker_2.board[(2, 1)]
        self.checker_2.board[(1, 2)].kind = 'knight'
        assert self.checker_2.check_end_of_game() == 'IM'


class TestGame:
    game = Game(True)
    board = Board({'white_turn': True, 'figures': {
        (0, 4): {'is_white': True, 'kind': 'king', 'status': 'S'},
        (0, 7): {'is_white': True, 'kind': 'rook', 'status': 'S'},
        (0, 0): {'is_white': True, 'kind': 'rook', 'status': 'S'},
        (6, 0): {'is_white': False, 'kind': 'pawn', 'status': 'S'},
        (0, 1): {'is_white': True, 'kind': 'knight', 'status': 'N'},
        (2, 2): {'is_white': False, 'kind': 'knight', 'status': 'N'},
        (4, 2): {'is_white': True, 'kind': 'pawn', 'status': 'N'},
        (4, 3): {'is_white': False, 'kind': 'pawn', 'status': 'E'},
    }})
    game.board = board

    def test__move_or_attack_0(self):
        rook = self.board.get((0, 0))
        self.game._move_or_attack(rook, (1, 0))
        assert not self.board.get((0, 0))
        assert self.board.get((1, 0)) == rook
        self.game._move_or_attack(rook, (3, 0))
        assert not self.board.get((1, 0))
        assert self.board.get((3, 0)) == rook
        self.game._move_or_attack(rook, (6, 0))
        assert not self.board.get((3, 0))
        assert self.board.get((6, 0)) == rook

    def test__move_or_attack_1(self):
        knight = self.board.get((0, 1))
        self.game._move_or_attack(knight, (2, 2))
        assert not self.board.get((0, 1))
        assert self.board.get((2, 2)) == knight
        self.game._move_or_attack(knight, (4, 1))
        assert not self.board.get((2, 2))
        assert self.board.get((4, 1)) == knight

    def test__castling(self):
        king = self.board.get((0, 4))
        rook = self.board.get((0, 7))
        self.game._castling(king, (0, 6), 'QC [(0, 5), (0, 6)] R (0, 7)')
        assert not self.board.get((0, 4))
        assert not self.board.get((0, 7))
        assert self.board.get((0, 6)) == king
        assert self.board.get((0, 5)) == rook

    def test__en_passant(self):
        pawn = self.board.get((4, 2))
        self.game._en_passant(pawn, (5, 3), 'AE P (4, 3)')
        assert not self.board.get((4, 3))
        assert not self.board.get((4, 2))
        assert self.board.get((5, 3)) == pawn
