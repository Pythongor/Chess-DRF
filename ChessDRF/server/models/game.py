from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from ..logic import Board, Checker
from .figure import Figure


class Game(models.Model):
    test = models.BooleanField(default=False)
    white_player = models.ForeignKey('ChessUser', on_delete=models.CASCADE, related_name='white')
    black_player = models.ForeignKey('ChessUser', on_delete=models.CASCADE, related_name='black')
    status = models.CharField(max_length=255, default="I")
    white_turn = models.BooleanField(null=True)
    has_transformation = models.BooleanField(default=False)
    white_message = models.CharField(max_length=255, null=True)
    black_message = models.CharField(max_length=255, null=True)

    @classmethod
    def create(cls, *args, **kwargs):
        game = Game.objects.create(*args, **kwargs)
        if kwargs['white_player'] == kwargs['black_player']:
            raise ValueError('Players can`t play with themselves')
        return game

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.board = Board(self)
        self.checker = Checker(self, self.board, getattr(self, 'test'))

    def create_dummy(self):
        dummy = Game.objects.create(test=True, white_player=self.white_player, black_player=self.black_player,
                                    status=self.status, white_turn=self.white_turn)
        board_dict = self.board.get_dict()
        dummy.board.initialize(board_dict)
        return dummy

    def turn(self, start=None, end=None, role=None):
        if self.has_transformation:
            if not self.transformation(role):
                return 'IS'
            else:
                self.white_turn = not self.white_turn
                self.status = 'S'
                self.has_transformation = False
                self.save()
        else:
            figure = self.board.get(*start)
            status = self.checker.check(figure, end)
            if status[0] != 'I':
                act_status = self.act(start, end, status)
                if act_status == 'T':
                    if not self.test:
                        self.has_transformation = True
                        self.status = 'T'
                        self.save()
                    return act_status
                else:
                    self.renew()
            else:
                return status

    def renew(self):
        self.white_turn = not self.white_turn
        self.save()
        try:
            figure = Figure.objects.get(game=self, is_white=self.white_turn, status='E')
            figure.status = 'N'
            figure.save()
        except ObjectDoesNotExist:
            pass

    def act(self, start, end, status):
        figure_id = self.board.get(*start).id
        if 'QC' in status:
            self._castling(start, end, status)
        elif 'AE' in status:
            self._en_passant(start, end, status)
        else:
            self._move_or_attack(start, end)
        if 'S' in status:
            figure = Figure.objects.get(id=figure_id)
            self.change_status(figure, status)
            if figure.status == 'T':
                return 'T'

    def _move_or_attack(self, start, end):
        self.board.move_figure(start, end)

    def _en_passant(self, start, end, status):
        pawn_pos = (int(status[6]), int(status[9]))
        self.board.move_figure(start, end)
        self.board.get(*pawn_pos).delete()

    def _castling(self, start, end, status):
        rook_pos = (int(status[-5]), int(status[-2]))
        rook_after_place_pos = (int(status[5]), int(status[8]))
        self.board.move_figure(start, end)
        self.board.move_figure(rook_pos, rook_after_place_pos)
        rook = self.board.get(*rook_after_place_pos)
        king = self.board.get(*end)
        king.status = rook.status = 'N'
        rook.save()
        king.save()

    def change_status(self, figure, str_status):
        if figure.role in ('king', 'rook') and figure.status == 'S':
            figure.status = 'N'
        elif figure.role == 'pawn':
            if 'QMS' in str_status and figure.status == 'S':
                figure.status = 'E'
            elif figure.status == 'S':
                figure.status = 'N'
            elif figure.status == 'N':
                figure.status = 'T'
            else:
                raise ValueError(f'{figure.role} {figure.status} "{str_status}"')
        else:
            raise ValueError
        figure.save()

    def transformation(self, role='queen'):
        if role in ('rook', 'bishop', 'knight', 'queen'):
            transformation_figure = Figure.objects.get(game=self, status='T')
            transformation_figure.status = 'N'
            transformation_figure.role = role
            transformation_figure.save()
            return role
