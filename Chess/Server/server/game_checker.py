from .models import Figure, Game


class GameChecker:
    def __init__(self, game):
        self.game = game

    def patch_request(self, turn):
        if self._end_of_game():
            return self._end_of_game()
        elif 'ERROR MESSAGE' in self.create_command(turn):
            return self.create_command(turn)
        else:
            return self.create_command(turn)

    def _end_of_game(self):
        if self._mate_checkup():
            if self._check_checkup():
                return {'GAME END': 'CHECKMATE'}
            else:
                return {'GAME END': 'STALEMATE'}
        elif self._insufficient_material_checkup():
            return {'GAME END': 'INSUFFICIENT DRAW'}

    def _mate_checkup(self):
        coordinates = [[i, j] for j in range(1, 9) for i in range(1, 9)]
        figures = Figure.objects.filter(game=self.game, is_white=self.game.white_turn)
        for figure in figures:
            for coord in coordinates:
                virtual = Game(status='VIRTUAL', white_player=self.game.white_player,
                               black_player=self.game.black_player,
                               white_turn=self.game.white_turn)
                virtual_checker = GameChecker(virtual)
                turn = [[figure.height, figure.width], coord]
                command = virtual_checker.create_command(turn)
                if 'ERROR MESSAGE' in command:
                    return False
        return True

    def _check_checkup(self):
        king = Figure.objects.filter(game=self.game, role='king',
                                     is_white=self.game.white_turn)
        return self._hit_checkup([king.height, king.width])

    def _insufficient_material_checkup(self):
        necessary_one = ('queen', 'pawn', 'rook')
        roles = self._list_of_figures(self.game.white_turn)
        if all([roles[figure] == 0 for figure in necessary_one]) and\
                roles['knight'] + roles['bishop'] < 2:
            return True
        return False

    def _list_of_figures(self, white):
        roles = {'king': 0, 'pawn': 0, 'queen': 0, 'rook': 0, 'bishop': 0, 'knight': 0}
        figures = Figure.objects.filter(game=self.game, is_white=white)
        for i in figures:
            roles[i.role] += 1
        return roles

    def create_command(self, turn):
        if self._get_figure(turn[0]):
            figure = self._get_figure(turn[0])
            if figure.is_white != self.game.white_turn:
                return {'ERROR MESSAGE': 'It is not your figure. Try again.'}
            elif self._checkup_move(figure, turn[1]) == 'ILLEGAL MOVE':
                return {'ERROR MESSAGE': 'Illegal move. Try again'}
            elif self._next_turn_modeling(self._checkup_move(figure, turn[1]), turn):
                return {'ERROR MESSAGE': 'Check! Try again.'}
            else:
                return self._checkup_move(figure, turn[1])
        else:
            return {'ERROR MESSAGE': 'There is no figure. Try again.'}

    def _get_figure(self, pos):
        if Figure.objects.filter(game=self.game, height=pos[0], width=pos[1]).exists():
            return Figure.objects.get(game=self.game, height=pos[0], width=pos[1])

    def _checkup_move(self, figure, move_to):
        command = figure.move_possibility(move_to)
        actions = {
            'ERROR': {'ILLEGAL MOVE': lambda x: 'ILLEGAL MOVE'},
            'COORDINATES': {'MOVE ATTACK': self._move_attack_checkup,
                            'MOVE ATTACK STATUS': self._move_attack_status_checkup,
                            'MOVE': self._move_checkup,
                            'ATTACK': self._attack_checkup},
            'QUERY': {'MOVE ATTACK': self._query_checkup,
                      'MOVE ATTACK STATUS': self._query_status_checkup,
                      'MOVE CASTLING': self._castling_checkup,
                      'MOVE': self._move_query_checkup}
        }
        for i in actions:
            if i in command:
                return actions[i][command['CHECKUP']](command[i])

    def _move_attack_checkup(self, move_to):
        if self._get_figure(move_to):
            figure = self._get_figure(move_to)
            turn = not self.game.white_turn if self.game.status == 'VIRTUAL' \
                else self.game.white_turn
            if figure.is_white != turn:
                return {'ATTACK ACCEPT': move_to}
            else:
                return {'ERROR': 'ILLEGAL MOVE'}
        else:
            return {'MOVE ACCEPT': move_to}

    def _move_attack_status_checkup(self, move_to):
        result = self._move_attack_checkup(move_to)
        for i in ('ATTACK ACCEPT', 'MOVE ACCEPT'):
            if i in result:
                result[i + ' STATUS'] = result[i]
                del result[i]
        return result

    def _move_checkup(self, move_to):
        if self._get_figure(move_to):
            return {'ERROR': 'ILLEGAL MOVE'}
        elif move_to[0] in (1, 8):
            return {'TRANSFORMATION': move_to}
        else:
            return {'MOVE ACCEPT': move_to}

    def _attack_checkup(self, move_to):
        if self._get_figure(move_to):
            figure = self._get_figure(move_to)
            if figure.is_white == self.game.white_turn:
                return {'ERROR': 'ILLEGAL MOVE'}
            elif move_to[0] in (1, 8):
                return {'TRANSFORMATION': move_to}
            else:
                return {'ATTACK ACCEPT': move_to}
        else:
            return self._en_passant_checkup(move_to)

    def _en_passant_checkup(self, move_to):
        index = {True: -1, False: 1}[getattr(self, 'white_turn')]
        if self._get_figure([move_to[0] + index, move_to[1]]):
            attacked = self._get_figure([move_to[0] + index, move_to[1]])
            if attacked.role == 'pawn' and attacked.status == 'EN PASSANT':
                return {'ACCEPT EN PASSANT': [move_to[0] + index, move_to[1]]}
            else:
                return {'ERROR': 'ILLEGAL MOVE'}
        else:
            return {'ERROR': 'ILLEGAL MOVE'}

    def _query_checkup(self, query):
        for _ in query[1:-1]:
            if any([i in self._move_attack_checkup(i) for i in ('ATTACK ACCEPT', 'ERROR')]):
                return {'ERROR': 'ILLEGAL MOVE'}
        return self._move_attack_checkup(query[-1])

    def _query_status_checkup(self, query):
        for _ in query[1:-1]:
            if any([i in self._move_attack_status_checkup(i) for i in (
                    'ATTACK ACCEPT', 'ERROR')]):
                return {'ERROR': 'ILLEGAL MOVE'}
        return self._move_attack_status_checkup(query[-1])

    def _castling_checkup(self, query):
        for i in query:
            if 'MOVE ACCEPT' not in self._move_attack_checkup(i):
                return {'ERROR': 'ILLEGAL MOVE'}
        for i in query[:3]:
            if self._hit_checkup(i):
                return {'ERROR': 'ILLEGAL MOVE'}
        coord = {(1, 2): '0', (1, 7): '1',
                 (8, 2): '2', (8, 7): '3'}[tuple(query[-1])]
        return {'CASTLING ACCEPT': coord}

    def _hit_checkup(self, coord):
        figures = Figure.objects.filter(game=self.game, is_white=not self.game.white_turn)
        for i in figures:
            if 'ERROR MESSAGE' not in self.create_command([[i.height, i.width], coord]):
                return True
        return False

    def _move_query_checkup(self, query):
        for i in query:
            if self._move_checkup(i) == {'ERROR': 'ILLEGAL MOVE'}:
                return {'ERROR': 'ILLEGAL MOVE'}
        return {'MOVE ACCEPT STATUS': query[-1]}

    def _next_turn_modeling(self, command, positions):
        virtual = Game(status='VIRTUAL', white_player=self.game.white_player,
                       black_player=self.game.black_player,
                       white_turn=self.game.white_turn)
        virtual_checker = GameChecker(virtual)
        return True
        # virtual = deepcopy(self)
        # virtual.board.mode = 'Virtual'
        # virtual._make_turn(command, positions)
        # return virtual._check_checkup(virtual.board.white_turn)
