import re
from copy import deepcopy


class Game:

    def __init__(self, dct='default'):
        if dct == 'default':
            dct = Board.default_dict
        self.board = Board(dct)

    def get_request(self, request):
        response = dict()
        response['figures'] = self.board.figures

    def patch_request(self, request):
        turn = request['turn']
        positions = Controller.parse_turn_string(turn)
        if self.create_command(positions) == 'Good!':
            pass
        else:
            return self.create_command(positions)

    def create_command(self, positions):
        if tuple(positions[0]) in self.board.figures:
            figure = self.board.figures[tuple(positions[0])]
            if figure.is_white != self.board.white_turn:
                return 'It is not your figure. Try again.'
            elif self._checkup_move(figure, positions[1]) == 'Cancel':
                return 'Illegal move. Try again.'
            elif self.next_turn_modeling(self._checkup_move(figure, positions[1]),
                                         positions):
                return 'Check! Try again.'
            else:
                return 'Good!'
        else:
            return'There is no figure. Try again.'

    def play(self):
        while True:
            if self._end_of_game():
                print(self._end_of_game())
                break
            View.show(self.board.figures)
            self._turn()

    def _turn(self):
        positions = Controller.default_turn_input(self.board.white_turn)
        command = None
        while command is None:
            command, positions = self._checkup_input(positions)
        self._make_turn(command, positions)
        self.board.reset_en_passants()
        self.board.white_turn = not self.board.white_turn

    def _checkup_input(self, positions, inpt=True):
        if tuple(positions[0]) in self.board.figures:
            figure = self.board.figures[tuple(positions[0])]
            if figure.is_white != self.board.white_turn and inpt:
                return None, Controller.turn_input('It is not your figure. Try again.')\
                    if inpt else None
            elif self._checkup_move(figure, positions[1]) == 'Cancel':
                return None, Controller.turn_input('Illegal move. Try again.')\
                    if inpt else None
            elif self.next_turn_modeling(self._checkup_move(figure, positions[1]),
                                         positions):
                return None, Controller.turn_input('Check! Try again.')\
                    if inpt else None
            else:
                return self._checkup_move(figure, positions[1]), positions
        else:
            return None, Controller.turn_input('There is no figure. Try again.')\
                if inpt else None

    def _checkup_move(self, figure, move_to):
        command = figure.move_possibility(move_to)
        status = ', change status' in command
        coordinates = self._exfoliate_query(command) if 'Query' in command else move_to
        actions = {
            'Illegal move': [lambda: 'Cancel', ],
            'Move/attack check': [self.board.move_attack_checkup, coordinates, status],
            'Move check': [self.board.move_checkup, coordinates],
            'Attack check': [self.board.attack_checkup, coordinates],
            'Query to move: ': [self.board.move_query_checkup, coordinates],
            'Query: ': [self.board.query_checkup, coordinates, status],
            'Query to castling': [self.castling_checkup, coordinates],
        }
        for i in actions:
            if i in command:
                if len(actions[i]) > 1:
                    return actions[i][0](*actions[i][1:])
                else:
                    return actions[i][0]()

    def next_turn_modeling(self, command, positions):
        virtual = deepcopy(self)
        virtual.board.mode = 'Virtual'
        virtual._make_turn(command, positions)
        return virtual._check_checkup(virtual.board.white_turn)

    def _check_checkup(self, white):
        for i in self.board.figures:
            if self.board.figures[i].role == 'king' and \
                    self.board.figures[i].is_white == white:
                return self.hit_checkup(i)

    # todo with re
    @staticmethod
    def _exfoliate_query(command):
        query = command.replace(
            'Query to move: ', '').replace('Query to castling: ', '').replace(
            'Query: ', '').replace(', change status', '')
        query = [[int(j) for j in i.split(', ')] for i in query[2:-2].split('], [')]
        return query

    def _make_turn(self, command, positions):
        status = ' change status' in command
        actions = {
            'Move accept': [self.board.move_or_attack, status],
            'Attack accept': [self.board.move_or_attack, status],
            'Castling accept ': [self.board.castling, command[-1]],
            'Accept en passant ': [self.board.en_passant,
                                   command[-7], command[-3]],
            'Transformation': [self.board.transformation, ],
        }
        for i in actions:
            if i in command:
                if len(actions[i]) == 1:
                    actions[i][0](positions)
                else:
                    actions[i][0](positions, *actions[i][1:])

    def _end_of_game(self):
        if self._mate_checkup():
            if self._check_checkup(self.board.white_turn):
                return 'Checkmate!'
            else:
                return 'Stalemate!'
        elif self._insufficient_material_checkup():
            return 'Draw! Neither player can checkmate opponent!'

    def _mate_checkup(self):
        coordinates = [[i, j] for j in 'abcdefgh' for i in range(1, 9)]
        for figure in self.board.figures:
            if self.board.figures[figure].is_white == self.board.white_turn:
                for coord in coordinates:
                    virtual = deepcopy(self)
                    positions = [tuple(figure), coord]
                    command, positions = virtual._checkup_input(positions, inpt=False)
                    if command is not None:
                        return False
        return True

    def hit_checkup(self, coord):
        coord = Figure.pos_mode(coord, str)
        for i in self.board.figures:
            if self.board.figures[i].is_white != self.board.white_turn:
                if self._checkup_input([i, coord], inpt=False)[0]:
                    return True
        return False

    def castling_checkup(self, query):
        for i in query:
            if self.board.destination_checkup(i) != 'Move accept':
                return 'Cancel'
        for i in query[:3]:
            if self.hit_checkup(i):
                return 'Cancel'
        coord = {(1, 2): '0', (1, 7): '1',
                 (8, 2): '2', (8, 7): '3'}[tuple(query[-1])]
        return 'Castling accept ' + coord

    def _insufficient_material_checkup(self):
        figures = self.board.list_of_figures(self.board.white_turn)
        necessary_one = ('queen', 'pawn', 'rook')
        if all(figures[figure] == 0 for figure in necessary_one) and\
                figures['knight'] + figures['bishop'] < 2:
            return 'Draw. Neither player has possibility to checkmate the opponent.'
        return False


class Board:
    height = range(1, 9)
    width = 'abcdefgh'
    default_dict = {
        'white_turn': True,
        'figures': {
            (1, 'a'): {'is_white': True, 'role': 'rook', 'status': 'Start'},
            (1, 'b'): {'is_white': True, 'role': 'knight', 'status': 'Normal'},
            (1, 'c'): {'is_white': True, 'role': 'bishop', 'status': 'Normal'},
            (1, 'd'): {'is_white': True, 'role': 'queen', 'status': 'Normal'},
            (1, 'e'): {'is_white': True, 'role': 'king', 'status': 'Start'},
            (1, 'f'): {'is_white': True, 'role': 'bishop', 'status': 'Normal'},
            (1, 'g'): {'is_white': True, 'role': 'knight', 'status': 'Normal'},
            (1, 'h'): {'is_white': True, 'role': 'rook', 'status': 'Start'},
            (2, 'a'): {'is_white': True, 'role': 'pawn', 'status': 'Normal'},
            (2, 'b'): {'is_white': True, 'role': 'pawn', 'status': 'Normal'},
            (2, 'c'): {'is_white': True, 'role': 'pawn', 'status': 'Normal'},
            (2, 'd'): {'is_white': True, 'role': 'pawn', 'status': 'Normal'},
            (2, 'e'): {'is_white': True, 'role': 'pawn', 'status': 'Normal'},
            (2, 'f'): {'is_white': True, 'role': 'pawn', 'status': 'Normal'},
            (2, 'g'): {'is_white': True, 'role': 'pawn', 'status': 'Normal'},
            (2, 'h'): {'is_white': True, 'role': 'pawn', 'status': 'Normal'},
            (7, 'a'): {'is_white': False, 'role': 'pawn', 'status': 'Normal'},
            (7, 'b'): {'is_white': False, 'role': 'pawn', 'status': 'Normal'},
            (7, 'c'): {'is_white': False, 'role': 'pawn', 'status': 'Normal'},
            (7, 'd'): {'is_white': False, 'role': 'pawn', 'status': 'Normal'},
            (7, 'e'): {'is_white': False, 'role': 'pawn', 'status': 'Normal'},
            (7, 'f'): {'is_white': False, 'role': 'pawn', 'status': 'Normal'},
            (7, 'g'): {'is_white': False, 'role': 'pawn', 'status': 'Normal'},
            (7, 'h'): {'is_white': False, 'role': 'pawn', 'status': 'Normal'},
            (8, 'a'): {'is_white': False, 'role': 'rook', 'status': 'Start'},
            (8, 'b'): {'is_white': False, 'role': 'knight', 'status': 'Normal'},
            (8, 'c'): {'is_white': False, 'role': 'bishop', 'status': 'Normal'},
            (8, 'd'): {'is_white': False, 'role': 'queen', 'status': 'Normal'},
            (8, 'e'): {'is_white': False, 'role': 'king', 'status': 'Start'},
            (8, 'f'): {'is_white': False, 'role': 'bishop', 'status': 'Normal'},
            (8, 'g'): {'is_white': False, 'role': 'knight', 'status': 'Normal'},
            (8, 'h'): {'is_white': False, 'role': 'rook', 'status': 'Start'},
        }
    }

    def __init__(self, dct):
        self.mode = 'Normal'
        self.white_turn = dct['white_turn']
        self.figures = dict()
        self._create_figures(dct['figures'])

    def _create_figures(self, figures):
        for i in figures:
            self._init_figure(figures[i]['is_white'], figures[i]['role'], i[0], i[1])

    def _init_figure(self, is_light, role, height, width):
        self.figures[(height, width)] = Figure(is_light, role, [height, width])

    def list_of_figures(self, white):
        figures = {'king': 0, 'pawn': 0, 'queen': 0, 'rook': 0, 'bishop': 0, 'knight': 0}
        for i in self.figures:
            if self.figures[i].is_white == white:
                figures[self.figures[i].role] += 1
        return figures

    def move_attack_checkup(self, move_to, status):
        status_string = {True: ' change status', False: ''}[status]
        result = self.destination_checkup(move_to)
        return self._cancel_handler(result, status_string)

    def destination_checkup(self, coord):
        turn = self.white_turn if self.mode == 'Normal' else not self.white_turn
        unit = Figure.pos_mode(coord, str)
        try:
            if self.figures[tuple(unit)].is_white != turn:
                return 'Attack accept'
            else:
                return 'Cancel'
        except KeyError:
            return 'Move accept'

    def move_checkup(self, move_to):
        try:
            self.figures[tuple(move_to)]
        except KeyError:
            if move_to[0] == 8 or move_to[0] == 1:
                return 'Transformation'
            else:
                return 'Move accept'
        else:
            return 'Cancel'

    def attack_checkup(self, move_to):
        try:
            if self.figures[tuple(move_to)].is_white == self.white_turn:
                return 'Cancel'
            else:
                if move_to[0] == 8 or move_to[0] == 1:
                    return 'Transformation'
                else:
                    return 'Attack accept'
        except KeyError:
            return self.en_passant_checkup(move_to)

    def en_passant_checkup(self, move_to):
        try:
            index = {True: -1, False: 1}[self.white_turn]
            figure_coord = [move_to[0] + index, move_to[1]]
            attacked = self.figures[tuple(figure_coord)]
            if attacked.role == 'pawn' and attacked.status == 'En passant':
                return 'Accept en passant ' + str(figure_coord)
            else:
                return 'Cancel'
        except KeyError:
            return 'Cancel'

    def move_query_checkup(self, query):
        for i in query:
            if self.move_checkup(i) == 'Cancel':
                return 'Cancel'
        return 'Move accept, change status'

    def query_checkup(self, query, status):
        status_string = {True: ' change status', False: ''}[status]
        for i in query[1:-1]:
            if self.destination_checkup(i) in ('Attack accept', 'Cancel'):
                return 'Cancel'
        return self._cancel_handler(self.destination_checkup(query[-1]), status_string)

    @staticmethod
    def _cancel_handler(reply, status):
        if reply == 'Cancel':
            return 'Cancel'
        else:
            return reply + status

    def move_or_attack(self, turn, status):
        self.figures[tuple(turn[1])] = self.figures[tuple(turn[0])]
        self.figures[tuple(turn[1])].pos = turn[1]
        del self.figures[tuple(turn[0])]
        if status:
            self._change_status(self.figures[tuple(turn[1])])

    @staticmethod
    def _change_status(figure):
        statuses = {
            ('pawn', 'Normal'): 'En passant',
            ('pawn', 'En passant'): 'Normal',
            ('king', 'Start'): 'Normal',
            ('rook', 'Start'): 'Normal',
        }
        figure.status = statuses[(figure.role, figure.status)]

    def transformation(self, turn, status):
        del status, self.figures[tuple(turn[0])]
        self._init_figure(
            self.white_turn, 'queen', turn[1][0], turn[1][1])

    def castling(self, turn, mode):
        modes = {'0': [[1, 'a'], [1, 'd']],
                 '1': [[1, 'h'], [1, 'f']],
                 '2': [[8, 'a'], [8, 'd']],
                 '3': [[8, 'h'], [8, 'f']]}
        positions = modes[mode]
        self.move_or_attack(positions, True)
        self.move_or_attack(turn, True)

    def en_passant(self, turn, height, width):
        height = int(height)
        self.figures[tuple(turn[1])] = self.figures[tuple(turn[0])]
        del self.figures[(height, width)], self.figures[tuple(turn[0])]

    def reset_en_passants(self):
        for i in self.figures:
            figure = self.figures[i]
            if figure.is_white != self.white_turn and figure.status == 'En passant':
                self._change_status(figure)


class Controller:
    @staticmethod
    def default_turn_input(white_turn):
        color = 'White' if white_turn else '\u001b[30mBlack\u001b[0m'
        positions = Controller.turn_input(
            color + ' turn. Enter turn in format "e2-e4".', False)
        return positions

    @staticmethod
    def turn_input(message, error=True):
        turn = input('\u001b[31m'+message+'\u001b[0m') if error else input(message)
        positions = Controller.parse_turn_string(turn)
        return positions

    @staticmethod
    def parse_turn_string(string):
        pattern = re.compile("^[A-Ha-h][1-8]-[A-Ha-h][1-8]$")
        while True:
            if pattern.match(string):
                positions = [[int(i[1]), i[0]] for i in string.split('-')]
                break
            else:
                string = input('\u001b[31mIncorrect format. Try again.\u001b[0m')
        return positions


class View:
    @staticmethod
    def show(figures):
        flag = True
        print('   ', end='')
        View._print_width_coordinates()
        for height in range(8, 0, -1):
            flag = View._print_row(figures, height, flag)
        print('   ', end='')
        View._print_width_coordinates()

    @staticmethod
    def _print_width_coordinates():
        for width in Board.width:
            print('\u001b[35m ' + str(width) + ' \u001b[0m', end='')
        print()

    @staticmethod
    def _print_row(figures, height, flag):
        View._print_height_coordinates(height)
        for width in Board.width:
            flag = View._print_tile(figures, height, width, flag)
        View._print_height_coordinates(height)
        print()
        return not flag

    @staticmethod
    def _print_height_coordinates(height):
        print('\u001b[35m ' + str(height) + ' \u001b[0m', end='')

    @staticmethod
    def _print_tile(figures, height, width, flag):
        color = {True: '\u001b[41m', False: '\u001b[42m'}[flag]
        try:
            to_print = color + ' ' + str(figures[(height, width)]) + ' \u001b[0m'
        except KeyError:
            to_print = color + '   \u001b[0m'
        print(to_print, end='')
        return not flag


class Figure:
    def __init__(self, is_white, role, pos):
        if role in ('king', 'rook'):
            self.status = 'Start'
        else:
            self.status = 'Normal'
        self.is_white = is_white
        self.role = role
        self.pos = pos

    def __str__(self, board_mode=True):
        if board_mode:
            return self._board_mode_str()
        else:
            color = {True: 'White', False: 'Black'}[self.is_white]
            return f'{color} {self.role} in {self.pos[1]}{self.pos[0]}'

    def _board_mode_str(self):
        symbol = {'bishop': 'B', 'king': '@', 'knight': 'K',
                  'pawn': 'P', 'rook': 'R', 'queen': 'Q'}[self.role]
        if self.is_white:
            color = ''
        else:
            color = '\u001b[30m'
        return color + symbol

    @staticmethod
    def pos_mode(pos, mode):
        if mode == str:
            return pos if type(pos[1]) == str else [pos[0], Board.width[pos[1]-1]]
        elif mode == int:
            return pos if type(pos[1]) == int else [pos[0], Board.width.index(pos[1])+1]

    def move_possibility(self, pos):
        if 1 <= pos[0] <= 8 and 1 <= Board.width.index(pos[1]) + 1 <= 8:
            moves = {
                'bishop': self._bishop_move_possibility,
                'king': self._king_move_possibility,
                'knight': self._knight_move_possibility,
                'pawn': self._pawn_move_possibility,
                'rook': self._rook_move_possibility,
                'queen': self._queen_move_possibility,
            }
            return moves[self.role]([pos[0], Board.width.index(pos[1]) + 1])
        else:
            raise ValueError

    def _bishop_move_possibility(self, pos):
        self_pos = self.pos_mode(self.pos, int)
        difference = [pos[0] - self_pos[0], pos[1] - self_pos[1]]
        if abs(difference[0]) == abs(difference[1]) != 0:
            query = self._query(pos, False)
            return f'Query: {query}'
        else:
            return 'Illegal move'

    def _query(self, pos, rook):
        self_pos = self.pos_mode(self.pos, int)
        if rook:
            direction = {self_pos[0] == pos[0] and self_pos[1] > pos[1]: (0, -1),
                         self_pos[0] == pos[0] and self_pos[1] < pos[1]: (0, 1),
                         self_pos[0] > pos[0] and self_pos[1] == pos[1]: (-1, 0),
                         self_pos[0] < pos[0] and self_pos[1] == pos[1]: (1, 0), }[True]
        else:
            direction = {self_pos[0] > pos[0] and self_pos[1] > pos[1]: (-1, -1),
                         self_pos[0] > pos[0] and self_pos[1] < pos[1]: (-1, 1),
                         self_pos[0] < pos[0] and self_pos[1] > pos[1]: (1, -1),
                         self_pos[0] < pos[0] and self_pos[1] < pos[1]: (1, 1), }[True]
        query = [self_pos, ]
        while pos not in query:
            coord = [query[-1][0]+direction[0], query[-1][1]+direction[1]]
            query.append(coord)
        return query

    def _knight_move_possibility(self, pos):
        self_pos = self.pos_mode(self.pos, int)
        difference = [pos[0] - self_pos[0], pos[1] - self_pos[1]]
        if (abs(difference[0]), abs(difference[1])) in ((1, 2), (2, 1)):
            return 'Move/attack check'
        else:
            return 'Illegal move'

    def _king_move_possibility(self, pos):
        self_pos = self.pos_mode(self.pos, int)
        difference = [pos[0] - self_pos[0], pos[1] - self_pos[1]]
        if (abs(difference[0]) <= 1 >= abs(difference[1])) and \
                (abs(difference[0]) | abs(difference[1])):
            if self.status == 'Start':
                return 'Move/attack check, change status'
            else:
                return 'Move/attack check'
        elif self.status == 'Start' and pos[1] in (3, 7) and \
                self_pos[0] == {True: 1, False: 8}[self.is_white]:
            query_coord = [{True: 1, False: 8}[self.is_white], {3: 2, 7: 7}[pos[1]]]
            query = self._query(query_coord, True)
            return f'Query to castling: {query}'
        else:
            return 'Illegal move'

    def _pawn_move_possibility(self, pos):
        self_pos = self.pos_mode(self.pos, int)
        ints = {True: [2, 4, 1, 8], False: [7, 5, -1, 1]}[self.is_white]
        if self_pos[0] == ints[0] and pos[0] == ints[1] and pos[1] == self_pos[1]:
            return f'Query to move: [[{self_pos[0]+1}, {pos[1]}], {pos}]'
        elif pos[0] == self.pos[0] + ints[2] and pos[1] == self_pos[1]:
            return 'Move check'
        elif pos[0] == self_pos[0] + ints[2] and abs(pos[1] - self_pos[1] == 1):
            return 'Attack check'
        else:
            return 'Illegal move'

    def _rook_move_possibility(self, pos):
        self_pos = self.pos_mode(self.pos, int)
        possible = (pos[0] == self_pos[0]) ^ (pos[1] == self_pos[1])
        if possible:
            query = self._query(pos, True)
            if self.status == 'Start':
                return f'Query: {query}, change status'
            else:
                return f'Query: {query}'
        else:
            return 'Illegal move'

    def _queen_move_possibility(self, pos):
        if self._bishop_move_possibility(pos) != 'Illegal move':
            return self._bishop_move_possibility(pos)
        else:
            return self._rook_move_possibility(pos).replace(', change status', '')


if __name__ == '__main__':
    game = Game()
    # game.play()
    while True:
        request = {'turn': None, 'user': None}
        View.show(game.board.figures)
        request['turn'] = input('\nTurn ->')
        game.make_request(request)
