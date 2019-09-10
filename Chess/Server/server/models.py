from django.db import models
from django.contrib.auth.models import User


class Game(models.Model):
    status = models.CharField(max_length=255, default="INVITED")
    white_player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='white')
    black_player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='black')
    white_turn = models.BooleanField(null=True)
    white_message = models.CharField(max_length=255, null=True)
    black_message = models.CharField(max_length=255, null=True)


class Figure(models.Model):
    DEFAULT_FIGURES = ('rook', 'knight', 'bishop', 'queen',
                       'king', 'bishop', 'knight', 'rook')
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    is_white = models.BooleanField()
    role = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    height = models.SmallIntegerField()
    width = models.SmallIntegerField()

    def move_possibility(self, pos):
        if 1 <= pos[0] <= 8 and 1 <= pos[1] <= 8:
            moves = {
                'bishop': self._bishop_move_possibility,
                'king': self._king_move_possibility,
                'knight': self._knight_move_possibility,
                'pawn': self._pawn_move_possibility,
                'rook': self._rook_move_possibility,
                'queen': self._queen_move_possibility,
            }
            return moves[getattr(self, 'role')](pos)
        else:
            raise ValueError

    def _bishop_move_possibility(self, pos):
        self_pos = [getattr(self, 'height'), getattr(self, 'width')]
        difference = [pos[0] - self_pos[0], pos[1] - self_pos[1]]
        if abs(difference[0]) == abs(difference[1]) != 0:
            query = self._query(pos, False)
            return {'CHECKUP': 'MOVE ATTACK', 'QUERY': query}
        else:
            return {'ERROR': 'ILLEGAL MOVE', 'CHECKUP': None}

    def _query(self, pos, rook):
        self_pos = [getattr(self, 'height'), getattr(self, 'width')]
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
        self_pos = [getattr(self, 'height'), getattr(self, 'width')]
        difference = [pos[0] - self_pos[0], pos[1] - self_pos[1]]
        if (abs(difference[0]), abs(difference[1])) in ((1, 2), (2, 1)):
            return {'CHECKUP': 'MOVE ATTACK', 'COORDINATES': pos}
        else:
            return {'ERROR': 'ILLEGAL MOVE'}

    def _king_move_possibility(self, pos):
        self_pos = [getattr(self, 'height'), getattr(self, 'width')]
        difference = [pos[0] - self_pos[0], pos[1] - self_pos[1]]
        if (abs(difference[0]) <= 1 >= abs(difference[1])) and \
                (abs(difference[0]) | abs(difference[1])):
            if getattr(self, 'status') == 'START':
                return {'CHECKUP': 'MOVE ATTACK STATUS', 'COORDINATES': pos}
            else:
                return {'CHECKUP': 'MOVE ATTACK', 'COORDINATES': pos}
        elif getattr(self, 'status') == 'START' and pos[1] in (3, 7) and \
                self_pos[0] == {True: 1, False: 8}[getattr(self, 'is_white')]:
            query_coord = [{True: 1, False: 8}[getattr(self, 'is_white')], {3: 2, 7: 7}[pos[1]]]
            query = self._query(query_coord, True)
            return {'CHECKUP': 'MOVE CASTLING', 'QUERY': query}
        else:
            return {'ERROR': 'ILLEGAL MOVE', 'CHECKUP': None}

    def _pawn_move_possibility(self, pos):
        self_pos = [getattr(self, 'height'), getattr(self, 'width')]
        ints = {True: [2, 4, 1, 8], False: [7, 5, -1, 1]}[getattr(self, 'is_white')]
        if self_pos[0] == ints[0] and pos[0] == ints[1] and pos[1] == self_pos[1]:
            return {'CHECKUP': 'MOVE', 'QUERY': [[self_pos[0]+1, pos[1]], pos]}
        elif pos[0] == self_pos[0] + ints[2] and pos[1] == self_pos[1]:
            return {'CHECKUP': 'MOVE', 'COORDINATES': pos}
        elif pos[0] == self_pos[0] + ints[2] and abs(pos[1] - self_pos[1] == 1):
            return {'CHECKUP': 'ATTACK', 'COORDINATES': pos}
        else:
            return {'ERROR': 'ILLEGAL MOVE', 'CHECKUP': None}

    def _rook_move_possibility(self, pos):
        self_pos = [getattr(self, 'height'), getattr(self, 'width')]
        possible = (pos[0] == self_pos[0]) ^ (pos[1] == self_pos[1])
        if possible:
            query = self._query(pos, True)
            if getattr(self, 'status') == 'START':
                return {'CHECKUP': 'MOVE ATTACK STATUS', 'QUERY': query}
            else:
                return {'CHECKUP': 'MOVE ATTACK', 'QUERY': query}
        else:
            return {'ERROR': 'ILLEGAL MOVE', 'CHECKUP': None}

    def _queen_move_possibility(self, pos):
        if self._bishop_move_possibility(pos) != {'ERROR': 'ILLEGAL MOVE'}:
            return self._bishop_move_possibility(pos)
        else:
            possibility = self._rook_move_possibility(pos)
            if 'ERROR' not in possibility:
                if ' STATUS' in possibility['CHECKUP']:
                    possibility['CHECKUP'].replace(' STATUS', '')
            return possibility
