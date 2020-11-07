from django.test.testcases import TestCase
from server.models import Figure, Game
from server.logic import Checker
from .mixins import ChessCaseMixin


class TestChecker(TestCase, ChessCaseMixin):
    def setup_class(self):
        super().setup_class(self)
        self.game = Game.objects.create(status='S', white_turn=True,
                                        white_player=self.white_player, black_player=self.black_player)
        self.checker = self.game.checker
        self.game_1 = Game.objects.create(status='S', white_turn=True,
                                          white_player=self.white_player, black_player=self.black_player)
        self.checker_1 = self.game_1.checker
        self.game_2 = Game.objects.create(status='S', white_turn=True,
                                          white_player=self.white_player, black_player=self.black_player)
        self.checker_2 = self.game_2.checker
        self.game.board.initialize()
        self.game_1.board.initialize({
            (0, 0): {'is_white': True, 'role': 'king', 'status': 'S'},
            (0, 2): {'is_white': False, 'role': 'rook', 'status': 'S'},
            (2, 0): {'is_white': False, 'role': 'rook', 'status': 'S'},
            (2, 2): {'is_white': False, 'role': 'bishop', 'status': 'N'},
        })
        self.game_2.board.initialize({
            (0, 0): {'is_white': True, 'role': 'king', 'status': 'S'},
            (1, 2): {'is_white': False, 'role': 'rook', 'status': 'S'},
            (2, 1): {'is_white': False, 'role': 'rook', 'status': 'S'},
        })

    def test__get_query(self):
        query = '[(2, 2), (4, 6)]'
        assert Checker._get_query(query) == [(2, 2), (4, 6)]

    def test__check_correct_figure_select(self):
        figure = self.game.board.get(0, 1)
        none = self.game.board.get(4, 1)
        enemy = self.game.board.get(7, 1)
        assert self.checker._check_correct_figure_select(figure, (2, 2)) == 'MA'
        assert self.checker._check_correct_figure_select(none, (2, 2)) == 'INF'
        assert self.checker._check_correct_figure_select(enemy, (5, 2)) == 'IFF'

    def test__check_move(self):
        assert self.checker._check_move(5, 5, 'status')
        assert not self.checker._check_move(0, 5, 'status')
        assert not self.checker._check_move(7, 5, 'status')

    def test__check_attack(self):
        assert not self.checker._check_attack(5, 5, 'status')
        assert not self.checker._check_attack(0, 5, 'status')
        assert self.checker._check_attack(7, 5, 'status')

    def test__check_move_and_attack(self):
        assert self.checker._check_move_and_attack(5, 5, 'status')
        assert not self.checker._check_move_and_attack(0, 5, 'status')
        assert self.checker._check_move_and_attack(7, 5, 'status')

    def test__check_move_query(self):
        assert not self.checker._check_move_query(2, 7, 'QM [(1, 6), (2, 7)]')
        assert not self.checker._check_move_query(5, 6, 'QM [(6, 6), (5, 7)]')
        assert self.checker._check_move_query(4, 0, 'QM [(4, 6), (4, 5), (4, 4), (4, 3), (4, 2), (4, 1), (4, 0)]')
        assert not self.checker._check_move_query(4, 0, 'QM [(2, 4), (3, 4), (4, 4), (5, 4), (6, 4)]')

    def test__check_move_and_attack_query(self):
        assert not self.checker._check_move_and_attack_query(2, 7, 'QMA [(1, 6), (2, 7)]')
        assert not self.checker._check_move_and_attack_query(5, 6, 'QMA [(6, 6), (5, 7)]')
        assert self.checker._check_move_and_attack_query(4, 0,
                                                         'QMA [(4, 6), (4, 5), (4, 4), (4, 3), (4, 2), (4, 1), (4, 0)]')
        assert self.checker._check_move_and_attack_query(4, 0, 'QMA [(2, 4), (3, 4), (4, 4), (5, 4), (6, 4)]')

    def test__check_castling(self):
        for i in (1, 2, 3, 5, 6):
            self.game.board.get(0, i).delete()
        for i in range(8):
            self.game.board.get(1, i).delete()
        self.game.board.get(6, 3).delete()
        assert self.checker._check_castling(0, 6, 'QC [(0, 5), (0, 6)] R (0, 7)')
        assert not self.checker._check_castling(0, 6, 'QC [(0, 3), (0, 2)] R (0, 0)')

    def test__check_trajectory(self):
        assert self.checker._check_trajectory(5, 5, 'M')
        assert not self.checker._check_trajectory(0, 5, 'M')
        assert not self.checker._check_trajectory(7, 5, 'M')
        assert not self.checker._check_trajectory(5, 5, 'A')
        assert not self.checker._check_trajectory(0, 5, 'A')
        assert self.checker._check_trajectory(7, 5, 'A')
        assert self.checker._check_trajectory(5, 5, 'MA')
        assert not self.checker._check_trajectory(0, 5, 'MA')
        assert self.checker._check_trajectory(7, 5, 'MA')
        assert not self.checker._check_trajectory(2, 7, 'QM [(1, 6), (2, 7)]')
        assert not self.checker._check_trajectory(5, 6, 'QM [(6, 6), (5, 7)]')
        assert self.checker._check_trajectory(4, 0, 'QM [(4, 6), (4, 5), (4, 4), (4, 3), (4, 2), (4, 1), (4, 0)]')
        assert not self.checker._check_trajectory(4, 0, 'QM [(2, 4), (3, 4), (4, 4), (5, 4), (6, 4)]')
        assert not self.checker._check_trajectory(2, 7, 'QMA [(1, 6), (2, 7)]')
        assert not self.checker._check_trajectory(5, 6, 'QMA [(6, 6), (5, 7)]')
        assert self.checker._check_trajectory(4, 0, 'QMA [(4, 6), (4, 5), (4, 4), (4, 3), (4, 2), (4, 1), (4, 0)]')
        assert self.checker._check_trajectory(4, 0, 'QMA [(2, 4), (3, 4), (4, 4), (5, 4), (6, 4)]')

    def test_is_tile_under_attack(self):
        assert not self.checker.is_tile_under_attack(0, 0)
        assert self.checker.is_tile_under_attack(5, 0)

    def test__is_act_danger_for_king(self):
        for i in (1, 2, 3, 5, 6):
            self.game.board.get(0, i).delete()
        for i in range(8):
            self.game.board.get(1, i).delete()
        self.game.board.get(6, 3).delete()
        king = self.checker.board.get(0, 4)
        assert self.checker._is_act_danger_for_king(king, (0, 3), 'M')

    def test__check_en_passant(self):
        self.game.board.move_figure((6, 0), (4, 0))
        pawn = self.game.board.get(4, 0)
        pawn.status = 'E'
        pawn.save()
        assert self.checker._check_en_passant(3, 0, 'AE P (4, 0)')

    def test_check_mate(self):
        assert self.checker_1.check_end_of_game() == 'M'
        self.game_1.board.move_figure((0, 2), (0, 1))
        assert not self.checker_1.check_end_of_game()

    def test_check_no_end(self):
        assert self.checker.check_end_of_game() is None

    def test_check_stalemate(self):
        assert self.checker_2.check_end_of_game() == 'SM'

    def test_check_insufficient(self):
        Figure.objects.get(game=self.game_2, height=2, width=1).delete()
        rook = self.checker_2.board.get(1, 2)
        rook.role = 'knight'
        rook.save()
        assert self.checker_2.check_end_of_game() == 'IM'
