from colorama import Fore
import re
from copy import deepcopy
from itertools import product

from ChessDRF.logic.board_and_controller import Controller
from ChessDRF.logic.figure import Figure


class Checker:
    def __init__(self, game, board, test: bool):
        self.game, self.board, self.test = game, board, test

    def check(self, figure, end: tuple, with_king_danger_check=True):
        status = self._check_correct_figure_select(figure, end)
        if status:
            if self._check_trajectory(end, status):
                if with_king_danger_check:
                    if not self._is_act_danger_for_king(figure, end, status):
                        if not self.test:
                            Controller.message('Good!')
                        return status
                    elif not self.test:
                        Controller.message('King under attack!', Fore.RED)
                else:
                    if not self.test:
                        Controller.message('Good!')
                    return status

    def _check_correct_figure_select(self, figure: Figure, pos: tuple):
        if not figure:
            if not self.test:
                Controller.message('No figure selected', Fore.RED)
        else:
            if figure.is_white != self.board.white_turn:
                if not self.test:
                    Controller.message('It`s not your figure', Fore.RED)
            else:
                return figure.move_check(pos)

    def _check_trajectory(self, pos: tuple, status: str):
        functions = (
            ('I' in status, lambda p, s: False),
            ('AE' in status, self._check_en_passant),
            ('QС' in status, self._check_castling),
            ('QMA' in status, self._check_move_and_attack_query),
            ('QM' in status, self._check_move_query),
            ('MA' in status, self._check_move_and_attack),
            ('M' in status, self._check_move),
            ('A' in status, self._check_attack),
        )
        for statement, func in functions:
            if statement:
                return func(pos, status)

    def _check_castling(self, _, status):
        str_query = re.findall(r' (.+) R', status)[0]
        query = self._get_query(str_query)
        for pos in query:
            if (not self._check_move(pos, status)) or self.is_tile_under_attack(pos):
                return False
        str_rook_pos = re.findall(r'R \((\d), (\d)\)', status)
        rook_pos = tuple(map(int, str_rook_pos[0]))
        rook = self.board[rook_pos]
        if rook.kind == 'rook' and rook.status == 'S':
            return True

    def _check_en_passant(self, end, status):
        pawn_pos = (int(status[6]), int(status[9]))
        if pawn := self.board.get(pawn_pos):
            if pawn.is_white != self.board.white_turn and pawn.status == 'E':
                return not bool(self.board.get(end))

    def _check_move_and_attack_query(self, end, status):
        str_query = re.findall(r' (.+)', status)[0]
        query = self._get_query(str_query)
        for pos in query[:-1]:
            if not self._check_move(pos, status):
                return False
        if self._check_move_and_attack(end, status):
            return True

    def _check_move_query(self, _, status):
        str_query = re.findall(r' (.+)', status)[0]
        query = self._get_query(str_query)
        for pos in query:
            if not self._check_move(pos, status):
                return False
        return True

    def _check_move_and_attack(self, end, status):
        return True if self._check_move(end, status) else self._check_attack(end, status)

    def _check_move(self, end, _):
        return not self.board.get(end)

    def _check_attack(self, end, _):
        if enemy := self.board.get(end):
            if enemy.is_white != self.board.white_turn:
                return True

    @staticmethod
    def _get_query(query):
        return [(int(i[0]), int(i[-1])) for i in query[2:-2].split('), (')]

    def is_tile_under_attack(self, pos):
        copy = deepcopy(self.game)
        copy.test = True
        copy.board.white_turn = not copy.board.white_turn
        for fig_pos, figure in self.board.items():
            if figure.is_white != self.board.white_turn:
                if copy.checker.check(figure, pos, False):
                    return True

    def _is_act_danger_for_king(self, figure, end, status):
        copy = deepcopy(self.game)
        copy_figure = copy.board[figure.pos]
        copy.act(copy_figure, end, status)
        return copy.checker.check_check()

    def check_check(self):
        king = self.board.get_king(self.board.white_turn)
        return self.is_tile_under_attack(king.pos)

    def check_end_of_game(self):
        if self._check_mate():
            return 'M' if self.check_check() else 'SM'
        if self._check_insufficient():
            return 'IM'

    def _check_mate(self):
        all_poses = product(range(8), range(8))
        for figure in filter(
                lambda f: f.is_white == self.board.white_turn, self.board.values()):
            for pos in all_poses:
                if (status := self.check(figure, pos)) and status != 'I':
                    return
        return True

    def _check_insufficient(self):
        white = black = 0
        for figure in self.board.values():
            if figure.kind in ('queen', 'rook', 'pawn'):
                return
            elif figure.kind in ('knight', 'bishop'):
                if figure.is_white:
                    white += 1
                else:
                    black += 1
        if max(white, black) < 2:
            return True
