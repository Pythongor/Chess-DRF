from colorama import Fore, Back, Style
import re
from .figure import Figure


class Board(dict):
    white_turn = None
    LETTERS = 'abcdefgh'
    default_dict = {
        'white_turn': True,
        'figures': {
            (0, 0): {'is_white': True, 'kind': 'rook', 'status': 'S'},
            (0, 1): {'is_white': True, 'kind': 'knight', 'status': 'N'},
            (0, 2): {'is_white': True, 'kind': 'bishop', 'status': 'N'},
            (0, 3): {'is_white': True, 'kind': 'queen', 'status': 'N'},
            (0, 4): {'is_white': True, 'kind': 'king', 'status': 'S'},
            (0, 5): {'is_white': True, 'kind': 'bishop', 'status': 'N'},
            (0, 6): {'is_white': True, 'kind': 'knight', 'status': 'N'},
            (0, 7): {'is_white': True, 'kind': 'rook', 'status': 'S'},
            (1, 0): {'is_white': True, 'kind': 'pawn', 'status': 'S'},
            (1, 1): {'is_white': True, 'kind': 'pawn', 'status': 'S'},
            (1, 2): {'is_white': True, 'kind': 'pawn', 'status': 'S'},
            (1, 3): {'is_white': True, 'kind': 'pawn', 'status': 'S'},
            (1, 4): {'is_white': True, 'kind': 'pawn', 'status': 'S'},
            (1, 5): {'is_white': True, 'kind': 'pawn', 'status': 'S'},
            (1, 6): {'is_white': True, 'kind': 'pawn', 'status': 'S'},
            (1, 7): {'is_white': True, 'kind': 'pawn', 'status': 'S'},
            (6, 0): {'is_white': False, 'kind': 'pawn', 'status': 'S'},
            (6, 1): {'is_white': False, 'kind': 'pawn', 'status': 'S'},
            (6, 2): {'is_white': False, 'kind': 'pawn', 'status': 'S'},
            (6, 3): {'is_white': False, 'kind': 'pawn', 'status': 'S'},
            (6, 4): {'is_white': False, 'kind': 'pawn', 'status': 'S'},
            (6, 5): {'is_white': False, 'kind': 'pawn', 'status': 'S'},
            (6, 6): {'is_white': False, 'kind': 'pawn', 'status': 'S'},
            (6, 7): {'is_white': False, 'kind': 'pawn', 'status': 'S'},
            (7, 0): {'is_white': False, 'kind': 'rook', 'status': 'S'},
            (7, 1): {'is_white': False, 'kind': 'knight', 'status': 'N'},
            (7, 2): {'is_white': False, 'kind': 'bishop', 'status': 'N'},
            (7, 3): {'is_white': False, 'kind': 'queen', 'status': 'N'},
            (7, 4): {'is_white': False, 'kind': 'king', 'status': 'S'},
            (7, 5): {'is_white': False, 'kind': 'bishop', 'status': 'N'},
            (7, 6): {'is_white': False, 'kind': 'knight', 'status': 'N'},
            (7, 7): {'is_white': False, 'kind': 'rook', 'status': 'S'},
        }
    }

    def __init__(self, dct=None):
        if dct is None:
            dct = self.default_dict
        super().__init__(self)
        self.create_from_dct(dct)

    def create_from_dct(self, dct):
        self.white_turn = dct['white_turn']
        for pos, figinfo in dct['figures'].items():
            figure = Figure(figinfo['is_white'], figinfo['kind'], figinfo['status'], pos)
            self[pos] = figure

    def get_from_pos(self, pos):
        if type(pos) == str:
            width = int(pos[1]) - 1
            height = self.LETTERS.index(pos[0])
        else:
            width = self.LETTERS.index(pos[1])
            height = int(pos[0]) - 1
        return height, width

    def move_figure(self, figure_pos, end_pos):
        figure = self[figure_pos]
        self[end_pos] = figure
        self.pop(figure_pos, None)
        figure.pos = end_pos

    def get_dict(self):
        dct = {'white_turn': self.white_turn, 'figures': {}}
        for pos, figure in self.items():
            fig_dict = {'is_white': figure.is_white, 'kind': figure.kind, 'pos': pos, 'status': figure.status}
            dct['figures'][pos] = fig_dict
        return dct

    def get_king(self, is_white: bool):
        for figure in self.values():
            if figure.kind == 'king' and figure.is_white == is_white:
                return figure


class Controller:
    @staticmethod
    def default_turn_input(white_turn):
        color = 'White' if white_turn else 'Black'
        positions = Controller.turn_input(f'{color} turn. Enter turn in format "e2-e4". ->', False)
        return positions

    @staticmethod
    def turn_input(message, error=True):
        turn = input('\u001b[31m' + message + '\u001b[0m') if error else input(message)
        positions = Controller.parse_turn_string(turn)
        return positions

    @staticmethod
    def parse_turn_string(string):
        pattern = re.compile("^[A-Ha-h][1-8]-[A-Ha-h][1-8]$")
        while True:
            if pattern.match(string):
                positions = [(int(i[1]) - 1, 'abcdefgah'.index(i[0].lower())) for i in string.split('-')]
                return positions
            else:
                string = input(f'{Fore.RED}Incorrect format. Try again.{Fore.RESET}\n->')

    @staticmethod
    def message(text, color=''):
        print(color, text, Style.RESET_ALL)

    @staticmethod
    def print_board(board):
        if board.white_turn:
            letters = ''.join(['   ', *[f' {letter} ' for letter in board.LETTERS], '\n'])
        else:
            letters = ''.join(['   ', *[f' {letter} ' for letter in reversed(board.LETTERS)], '\n'])
        rows = [letters]
        print()
        for i in range(8):
            r = [f' {i + 1} ']
            for j in range(8):
                tile = board.get((i, j), ' ')
                back = Back.RED if (i + j) % 2 else Back.GREEN
                r.append(back + ' ' + str(tile) + ' ')
            r.append(f' {i + 1} ')
            if not board.white_turn:
                r.reverse()
            r[-2] = ''.join((r[-2], Style.RESET_ALL))
            r = ''.join((*r, '\n'))
            rows.append(r)
        rows.append(letters)
        if board.white_turn:
            rows.reverse()
        print(''.join(rows))
