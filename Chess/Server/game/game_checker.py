from .models import Figure


class GameChecker:
    def __init__(self, game):
        self.game = game

    def patch_request(self, turn):
        if 'ERROR MESSAGE' in self.create_command(turn):
            return self.create_command(turn)
        else:
            return self.create_command(turn)

    def create_command(self, turn):
        if self.get_figure(turn[0]):
            figure = self.get_figure(turn[0])
            if figure.is_white != self.game.white_turn:
                return {'ERROR MESSAGE': 'It is not your figure. Try again.'}
            elif self._checkup_move(figure, turn[1]) == 'ILLEGAL MOVE':
                return {'ERROR MESSAGE': 'Illegal move. Try again'}
            # elif self.next_turn_modeling(self._checkup_move(figure, turn[1]),
            #                              turn):
            #     return 'Check! Try again.'
            else:
                return self._checkup_move(figure, turn[1])
        else:
            return {'ERROR MESSAGE': 'There is no figure. Try again.'}

    def get_figure(self, pos):
        if Figure.objects.filter(game=self.game, height=pos[0], width=pos[1]).exists():
            return Figure.objects.get(game=self.game, height=pos[0], width=pos[1])

    def _checkup_move(self, figure, move_to):
        command = figure.move_possibility(move_to)
        actions = {
            'ERROR': {'ILLEGAL MOVE': lambda x: 'ILLEGAL MOVE'},
            'COORDINATES': {'MOVE ATTACK': self.move_attack_checkup,
                            'MOVE ATTACK STATUS': self.move_attack_status_checkup,
                            'MOVE': self.move_checkup,
                            'ATTACK': self.attack_checkup},
            'QUERY': {'MOVE ATTACK': self.query_checkup,
                      'MOVE ATTACK STATUS': self.query_status_checkup,
                      'MOVE CASTLING': self.castling_checkup,
                      'MOVE': self.move_query_checkup}
        }
        for i in actions:
            if i in command:
                return actions[i][command['CHECKUP']](command[i])

    def move_attack_checkup(self, move_to):
        if self.get_figure(move_to):
            figure = self.get_figure(move_to)
            turn = not self.game.white_turn if self.game.status == 'MODELING' \
                else self.game.white_turn
            if figure.is_white != turn:
                return {'ATTACK ACCEPT': move_to}
            else:
                return {'ERROR': 'ILLEGAL MOVE'}
        else:
            return {'MOVE ACCEPT': move_to}

    def move_attack_status_checkup(self, move_to):
        result = self.move_attack_checkup(move_to)
        for i in ('ATTACK ACCEPT', 'MOVE ACCEPT'):
            if i in result:
                result[i + ' STATUS'] = result[i]
                del result[i]
        return result

    def move_checkup(self, move_to):
        if self.get_figure(move_to):
            return {'ERROR': 'ILLEGAL MOVE'}
        elif move_to[0] in (1, 8):
            return {'TRANSFORMATION': move_to}
        else:
            return {'MOVE ACCEPT': move_to}

    def attack_checkup(self, move_to):
        if self.get_figure(move_to):
            figure = self.get_figure(move_to)
            if figure.is_white == self.game.white_turn:
                return {'ERROR': 'ILLEGAL MOVE'}
            elif move_to[0] in (1, 8):
                return {'TRANSFORMATION': move_to}
            else:
                return {'ATTACK ACCEPT': move_to}
        else:
            return self.en_passant_checkup(move_to)

    def en_passant_checkup(self, move_to):
        index = {True: -1, False: 1}[getattr(self, 'white_turn')]
        if self.get_figure([move_to[0] + index, move_to[1]]):
            attacked = self.get_figure([move_to[0] + index, move_to[1]])
            if attacked.role == 'pawn' and attacked.status == 'EN PASSANT':
                return {'ACCEPT EN PASSANT': [move_to[0] + index, move_to[1]]}
            else:
                return {'ERROR': 'ILLEGAL MOVE'}
        else:
            return {'ERROR': 'ILLEGAL MOVE'}

    def query_checkup(self, query):
        for _ in query[1:-1]:
            if any([i in self.move_attack_checkup(i) for i in ('ATTACK ACCEPT', 'ERROR')]):
                return {'ERROR': 'ILLEGAL MOVE'}
        return self.move_attack_checkup(query[-1])

    def query_status_checkup(self, query):
        for _ in query[1:-1]:
            if any([i in self.move_attack_status_checkup(i) for i in ('ATTACK ACCEPT', 'ERROR')]):
                return {'ERROR': 'ILLEGAL MOVE'}
        return self.move_attack_status_checkup(query[-1])

    def castling_checkup(self, query):
        for i in query:
            if 'MOVE ACCEPT' not in self.move_attack_checkup(i):
                return {'ERROR': 'ILLEGAL MOVE'}
        for i in query[:3]:
            if self.hit_checkup(i):
                return {'ERROR': 'ILLEGAL MOVE'}
        coord = {(1, 2): '0', (1, 7): '1',
                 (8, 2): '2', (8, 7): '3'}[tuple(query[-1])]
        return {'CASTLING ACCEPT': coord}

    def hit_checkup(self, coord):
        figures = Figure.objects.filter(game=self.game, is_white=not self.game.white_turn)
        for i in figures:
            if 'ERROR MESSAGE' not in self.create_command([[i.height, i.width], coord]):
                return True
        return False

    def move_query_checkup(self, query):
        for i in query:
            if self.move_checkup(i) == {'ERROR': 'ILLEGAL MOVE'}:
                return {'ERROR': 'ILLEGAL MOVE'}
        return {'MOVE ACCEPT STATUS': query[-1]}


"""
 * @param parameter2 documentation
 * @param parameter3 documentation
 * @param parameter4 documentation
"""