import re
from itertools import product
from ..models import Figure


class Checker:
    def __init__(self, game, board, test: bool):
        self.game, self.board, self.test = game, board, test

    def check(self, figure, end: tuple, with_king_danger_check=True):
        status = self._check_correct_figure_select(figure, end)
        if status not in ('INF', 'IFF'):
            if new_status := self._check_trajectory(*end, status):
                if with_king_danger_check:
                    if not self._is_act_danger_for_king(figure, end, new_status):
                        return new_status
                    else:
                        return 'IC'
                else:
                    return new_status
            else:
                return 'IM'
        else:
            return status

    def _check_correct_figure_select(self, figure: Figure, pos: tuple):
        if not figure:
            return 'INF'
        else:
            if figure.is_white != self.game.white_turn:
                return 'IFF'
            else:
                return figure.move_check(*pos)

    def _check_trajectory(self, height, width, status: str):
        functions = (
            ('I' in status, lambda h, w, s: False),
            ('AE' in status, self._check_en_passant),
            ('QC' in status, self._check_castling),
            ('QMA' in status, self._check_move_and_attack_query),
            ('QM' in status, self._check_move_query),
            ('MA' in status, self._check_move_and_attack),
            ('M' in status, self._check_move),
            ('A' in status, self._check_attack),
        )
        for statement, func in functions:
            if statement:
                return func(height, width, status)

    def _check_castling(self, height, width, status):
        str_query = re.findall(r' (.+) R', status)[0]
        query = self._get_query(str_query)
        for pos in query:
            if (not self._check_move(*pos, status)) or self.is_tile_under_attack(*pos):
                return False
        str_rook_pos = re.findall(r'R \((\d), (\d)\)', status)
        rook_pos = tuple(map(int, str_rook_pos[0]))
        rook = self.board.get(*rook_pos)
        if rook.role == 'rook' and rook.status == 'S' and rook.is_white == self.game.white_turn:
            return status

    def _check_en_passant(self, height, width, status):
        pawn_pos = (int(status[6]), int(status[9]))
        if pawn := self.board.get(*pawn_pos):
            if pawn.is_white != self.game.white_turn and pawn.status == 'E':
                if not bool(self.board.get(height, width)):
                    return status
                return not bool(self.board.get(height, width))
        else:
            pawn_pos_2 = int(status[14]), int(status[17])
            return self._check_attack(*pawn_pos_2, 'A')

    def _check_move_and_attack_query(self, height, width, status):
        str_query = re.findall(r' (.+)', status)[0]
        query = self._get_query(str_query)
        for pos in query[:-1]:
            if not self._check_move(*pos, status):
                return False
        if self._check_move_and_attack(height, width, status):
            return status

    def _check_move_query(self, _, __, status):
        str_query = re.findall(r' (.+)', status)[0]
        query = self._get_query(str_query)
        for pos in query:
            if not self._check_move(*pos, status):
                return False
        return status

    def _check_move_and_attack(self, height, width, status):
        move = self._check_move(height, width, status)
        attack = self._check_attack(height, width, status)
        return move or attack

    def _check_move(self, height, width, status):
        if not self.board.get(height, width):
            return status

    def _check_attack(self, height, width, status):
        if enemy := self.board.get(height, width):
            if enemy.is_white != self.game.white_turn:
                return status

    @staticmethod
    def _get_query(query):
        return [(int(i[0]), int(i[-1])) for i in query[2:-2].split('), (')]

    def is_tile_under_attack(self, height, width):
        dummy = self.game.create_dummy()
        dummy.white_turn = not dummy.white_turn
        for figure in Figure.objects.filter(game=dummy, is_white=dummy.white_turn):
            if dummy.checker.check(figure, (height, width), False)[0] != 'I':
                dummy.delete()
                return True
        dummy.delete()

    def _is_act_danger_for_king(self, figure, end, status):
        dummy = self.game.create_dummy()
        dummy.act((figure.height, figure.width), end, status)
        is_act_danger_for_king = dummy.checker.check_check()
        dummy.delete()
        return is_act_danger_for_king

    def check_check(self):
        king = self.board.get_king(self.game.white_turn)
        return self.is_tile_under_attack(king.height, king.width)

    def check_end_of_game(self):
        if self._check_mate():
            return 'M' if self.check_check() else 'SM'
        if self._check_insufficient():
            return 'IM'

    def _check_mate(self):
        all_poses = list(product(range(8), range(8)))
        for figure in Figure.objects.filter(game=self.game, is_white=self.game.white_turn):
            for pos in all_poses:
                if self.check(figure, pos)[0] != 'I':
                    return
        return True

    def _check_insufficient(self):
        white = black = 0
        for figure in Figure.objects.filter(game=self.game):
            if figure.role in ('queen', 'rook', 'pawn'):
                # print(f'{figure} {figure.height=} {figure.width=} {figure.is_white=} {figure.role=}')
                return
            elif figure.role in ('knight', 'bishop'):
                if figure.is_white:
                    white += 1
                else:
                    black += 1
        if max(white, black) < 2:
            return True
