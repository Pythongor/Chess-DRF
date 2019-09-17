from .models import Figure, Game


class GameChecker:
    def __init__(self, game):
        self.game = game

    def patch_request(self, turn):
        if self._end_of_game():
            return self._end_of_game()
        elif self.check_checkup():
            return {'ERROR MESSAGE': 'Check! Try again.'}
        if 'ERROR MESSAGE' in self.create_command(turn):
            return self.create_command(turn)
        else:
            return self.create_command(turn)

    def _end_of_game(self):
        if self._mate_checkup():
            if self.check_checkup():
                return {'GAME END': 'CHECKMATE',
                        'WINNER': self.game.white_player.username if not
                        self.game.white_turn else self.game.black_player.username}
            else:
                return {'GAME END': 'DRAW'}
        elif self._insufficient_material_checkup():
            return {'GAME END': 'DRAW'}

    def _mate_checkup(self):
        coordinates = [[i, j] for j in range(1, 9) for i in range(1, 9)]
        figures = Figure.objects.filter(game=self.game, is_white=self.game.white_turn)
        king = Figure.objects.filter(game=self.game, is_white=self.game.white_turn,
                                     role='king').exists
        if not king:
            return True
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

    def check_checkup(self):
        print(self.game.white_turn)
        try:
            king = Figure.objects.get(game=self.game, role='king',
                                      is_white=self.game.white_turn)
        except Figure.DoesNotExist:
            return False
        print([king.height, king.width])
        response = self._hit_checkup([king.height, king.width])
        # print(response)
        return response

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

    def create_command(self, turn, normal=True):
        if self.get_figure(turn[0]):
            figure = self.get_figure(turn[0])
            if figure.is_white != self.game.white_turn and normal:
                return {'ERROR MESSAGE': 'It is not your figure. Try again.'}
            elif self._checkup_move(figure, turn[1], not normal) == {'ERROR':
                                                                     'ILLEGAL MOVE'}:
                return {'ERROR MESSAGE': 'Illegal move. Try again'}
            else:
                return self._checkup_move(figure, turn[1], not normal)
        else:
            return {'ERROR MESSAGE': 'There is no figure. Try again.'}

    def get_figure(self, pos, get=True):
        if Figure.objects.filter(game=self.game, height=pos[0], width=pos[1]).exists():
            if get:
                return Figure.objects.get(game=self.game, height=pos[0], width=pos[1])
            else:
                return Figure.objects.filter(game=self.game, height=pos[0], width=pos[1])

    def _checkup_move(self, figure, move_to, reverse=False):
        command = figure.move_possibility(move_to)
        # print(command)
        actions = {
            'ERROR': {'ILLEGAL MOVE': lambda x, y, z: {'ERROR': 'ILLEGAL MOVE'},
                      None: lambda x, y, z: {'ERROR': 'ILLEGAL MOVE'}},
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
                coords = [figure.height, figure.width]
                return actions[i][command['CHECKUP']](coords, command[i], reverse)

    def _move_attack_checkup(self, coords, move_to, reverse):
        if self.get_figure(move_to):
            figure = self.get_figure(move_to)
            turn = not self.game.white_turn if reverse \
                else self.game.white_turn
            if figure.is_white != turn and self.game.status == 'STARTED':
                return {'ATTACK ACCEPT': [coords, move_to]}
            else:
                print('((', self.game.status, figure.is_white)
                return {'ERROR': 'ILLEGAL MOVE'}
        else:
            return {'MOVE ACCEPT': [coords, move_to]}

    def _move_attack_status_checkup(self, coords, move_to, reverse):
        result = self._move_attack_checkup(coords, move_to, reverse)
        for i in ('ATTACK ACCEPT', 'MOVE ACCEPT'):
            if i in result:
                result[i + ' STATUS'] = result[i]
                del result[i]
        return result

    def _move_checkup(self, coords, move_to, reverse):
        if self.get_figure(move_to):
            return {'ERROR': 'ILLEGAL MOVE'}
        elif move_to[0] in (1, 8):
            return {'MOVE TRANSFORMATION': [coords, move_to]}
        else:
            return {'MOVE ACCEPT': [coords, move_to]}

    def _attack_checkup(self, coords, move_to, reverse):
        if self.get_figure(move_to):
            figure = self.get_figure(move_to)
            if figure.is_white == self.game.white_turn:
                return {'ERROR': 'ILLEGAL MOVE'}
            elif move_to[0] in (1, 8):
                return {'ATTACK TRANSFORMATION': [coords, move_to]}
            else:
                return {'ATTACK ACCEPT': [coords, move_to]}
        else:
            return self._en_passant_checkup(coords, move_to, reverse)

    def _en_passant_checkup(self, coords, move_to, reverse):
        index = {True: -1, False: 1}[self.game.white_turn]
        if self.get_figure([move_to[0] + index, move_to[1]]):
            attacked = self.get_figure([move_to[0] + index, move_to[1]])
            if attacked.role == 'pawn' and attacked.status == 'EN PASSANT':
                return {'ACCEPT EN PASSANT': [
                    coords, [move_to[0] + index, move_to[1]], move_to]}
            else:
                return {'ERROR': 'ILLEGAL MOVE'}
        else:
            return {'ERROR': 'ILLEGAL MOVE'}

    def _query_checkup(self, coords, query, reverse):
        for pos in query[1:-1]:
            if any([i in self._move_attack_checkup(coords, pos, reverse) for i in (
                    'ATTACK ACCEPT', 'ERROR')]):
                return {'ERROR': 'ILLEGAL MOVE'}
        return self._move_attack_checkup(coords, query[-1], reverse)

    def _query_status_checkup(self, coords, query, reverse):
        for pos in query[1:-1]:
            if any([i in self._move_attack_status_checkup(coords, pos, reverse) for i in (
                    'ATTACK ACCEPT', 'ERROR')]):
                return {'ERROR': 'ILLEGAL MOVE'}
        return self._move_attack_status_checkup(coords, query[-1], reverse)

    def _castling_checkup(self, coords, query, reverse):
        for i in query[1::]:
            if 'MOVE ACCEPT' not in self._move_attack_checkup(coords, i, reverse):
                print('can`t go:', i)
                return {'ERROR': 'ILLEGAL MOVE'}
        for i in query[:3]:
            if self._hit_checkup(i):
                return {'ERROR': 'ILLEGAL MOVE'}
        coord = {(1, 2): '0', (1, 7): '1',
                 (8, 2): '2', (8, 7): '3'}[tuple(query[-1])]
        return {'CASTLING ACCEPT': [[coords, query[-1]], coord]}

    def _hit_checkup(self, coord):
        figures = Figure.objects.filter(game=self.game, is_white=not self.game.white_turn)
        for i in figures:
            command = self.create_command([[i.height, i.width], coord], False)
            print('figure: ', i.height, i.width, command)
            if 'ERROR MESSAGE' not in command:
                return True
        return False

    def _move_query_checkup(self, coords, query, reverse):
        for i in query:
            if self._move_checkup(coords, i, reverse) == {'ERROR': 'ILLEGAL MOVE'}:
                return {'ERROR': 'ILLEGAL MOVE'}
        return {'MOVE ACCEPT STATUS': [coords, query[-1]]}
