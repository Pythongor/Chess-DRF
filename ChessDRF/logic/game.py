from colorama import Fore
from copy import deepcopy

from ChessDRF.logic.board_and_controller import Board, Controller
from ChessDRF.logic.checker import Checker


class Game:
    def __init__(self, test=False):
        self.board = Board()
        self.test = False
        self.checker = Checker(self, self.board, test)

    def __deepcopy__(self, memo):
        copy = Game()
        copy.test = self.test
        copy.board = deepcopy(self.board)
        copy.checker = Checker(copy, copy.board, copy.test)
        return copy

    def play(self):
        while True:
            Controller.print_board(self.board)
            self.turn()

    def turn(self):
        start, end = Controller.default_turn_input(self.board.white_turn)
        figure = self.board[start]
        if status := self.checker.check(figure, end):
            self.act(figure, end, status)
            self.renew()
        else:
            self.turn()

    def renew(self):
        self.board.white_turn = not self.board.white_turn
        for figure in self.board.values():
            if figure.is_white and figure.status == 'E':
                figure.status = 'N'

    def act(self, figure, end, status):
        if 'QC' in status:
            self._castling(figure, end, status)
        if 'AE' in status:
            self._en_passant(figure, end, status)
        else:
            self._move_or_attack(figure, end)
        if 'S' in status:
            self.change_status(figure, status)

    def _move_or_attack(self, figure, end):
        self.board.move_figure(figure.pos, end)

    def _castling(self, figure, end, status):
        rook_pos = (int(status[-5]), int(status[-2]))
        rook_after_place_pos = (int(status[5]), int(status[8]))
        rook = self.board[rook_pos]
        self.board.move_figure(figure.pos, end)
        self.board.move_figure(rook_pos, rook_after_place_pos)
        figure.status = rook.status = 'N'

    def _en_passant(self, figure, end, status):
        pawn_pos = (int(status[6]), int(status[9]))
        self.board.move_figure(figure.pos, end)
        self.board.pop(pawn_pos)

    def change_status(self, figure, str_status):
        if figure.kind in ('king', 'rook') and figure.status == 'S':
            figure.status = 'N'
        elif figure.kind == 'pawn':
            if 'QMS' in str_status and figure.status == 'S':
                figure.status = 'E'
            elif figure.status == 'S':
                figure.status = 'N'
            elif figure.status == 'N':
                figure.kind = self.transformation()
            else:
                raise ValueError(f'{figure.kind} {figure.status} "{str_status}"')
        else:
            raise ValueError

    def transformation(self):
        if not self.test:
            kind = input('Select figure type to transform (rook, bishop, knight or queen) ->').lower()
            if kind not in ('rook', 'bishop', 'knight', 'queen'):
                Controller.message('Illegal figure!', Fore.RED)
                return self.transformation()
            else:
                return kind
        else:
            return 'queen'
    

if __name__ == '__main__':
    g = Game()
    g.play()
