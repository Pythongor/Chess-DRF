from itertools import product
from server.models import Figure
from django.core.exceptions import ObjectDoesNotExist


class Board:
    """class for managing figures"""
    LETTERS = 'abcdefgh'
    DEFAULT_DICT = {
        (0, 0): {'is_white': True, 'role': 'rook', 'status': 'S'},
        (0, 1): {'is_white': True, 'role': 'knight', 'status': 'N'},
        (0, 2): {'is_white': True, 'role': 'bishop', 'status': 'N'},
        (0, 3): {'is_white': True, 'role': 'queen', 'status': 'N'},
        (0, 4): {'is_white': True, 'role': 'king', 'status': 'S'},
        (0, 5): {'is_white': True, 'role': 'bishop', 'status': 'N'},
        (0, 6): {'is_white': True, 'role': 'knight', 'status': 'N'},
        (0, 7): {'is_white': True, 'role': 'rook', 'status': 'S'},
        (1, 0): {'is_white': True, 'role': 'pawn', 'status': 'S'},
        (1, 1): {'is_white': True, 'role': 'pawn', 'status': 'S'},
        (1, 2): {'is_white': True, 'role': 'pawn', 'status': 'S'},
        (1, 3): {'is_white': True, 'role': 'pawn', 'status': 'S'},
        (1, 4): {'is_white': True, 'role': 'pawn', 'status': 'S'},
        (1, 5): {'is_white': True, 'role': 'pawn', 'status': 'S'},
        (1, 6): {'is_white': True, 'role': 'pawn', 'status': 'S'},
        (1, 7): {'is_white': True, 'role': 'pawn', 'status': 'S'},
        (6, 0): {'is_white': False, 'role': 'pawn', 'status': 'S'},
        (6, 1): {'is_white': False, 'role': 'pawn', 'status': 'S'},
        (6, 2): {'is_white': False, 'role': 'pawn', 'status': 'S'},
        (6, 3): {'is_white': False, 'role': 'pawn', 'status': 'S'},
        (6, 4): {'is_white': False, 'role': 'pawn', 'status': 'S'},
        (6, 5): {'is_white': False, 'role': 'pawn', 'status': 'S'},
        (6, 6): {'is_white': False, 'role': 'pawn', 'status': 'S'},
        (6, 7): {'is_white': False, 'role': 'pawn', 'status': 'S'},
        (7, 0): {'is_white': False, 'role': 'rook', 'status': 'S'},
        (7, 1): {'is_white': False, 'role': 'knight', 'status': 'N'},
        (7, 2): {'is_white': False, 'role': 'bishop', 'status': 'N'},
        (7, 3): {'is_white': False, 'role': 'queen', 'status': 'N'},
        (7, 4): {'is_white': False, 'role': 'king', 'status': 'S'},
        (7, 5): {'is_white': False, 'role': 'bishop', 'status': 'N'},
        (7, 6): {'is_white': False, 'role': 'knight', 'status': 'N'},
        (7, 7): {'is_white': False, 'role': 'rook', 'status': 'S'},
    }

    def __init__(self, game):
        self.game = game

    def initialize(self, dct=None):
        if dct is None:
            dct = self.DEFAULT_DICT
        self.create_figures(dct)

    def create_figures(self, dct):
        Figure.objects.filter(game=self.game).delete()
        for pos, fig_data in dct.items():
            Figure.objects.create(
                is_white=fig_data['is_white'], role=fig_data['role'],
                status=fig_data['status'], height=pos[0], width=pos[1], game=self.game
            )

    def get_from_pos(self, pos):
        if type(pos) == str:
            width = int(pos[1]) - 1
            height = self.LETTERS.index(pos[0])
        else:
            width = self.LETTERS.index(pos[1])
            height = int(pos[0]) - 1
        return height, width

    def move_figure(self, figure_pos, end_pos):
        try:
            old_figure = Figure.objects.get(height=end_pos[0], width=end_pos[1], game=self.game)
            old_figure.delete()
        except ObjectDoesNotExist:
            pass
        figure = Figure.objects.get(height=figure_pos[0], width=figure_pos[1], game=self.game)
        f_id = figure.id
        f = Figure.objects.get(id=f_id)
        f.height = end_pos[0]
        f.width = end_pos[1]
        f.save()

    def get_dict(self):
        dct = dict()
        for figure in Figure.objects.filter(game=self.game):
            fig_dict = {'is_white': figure.is_white, 'role': figure.role, 'status': figure.status}
            pos = (getattr(figure, 'height'), getattr(figure, 'width'))
            dct[pos] = fig_dict
        return dct

    def get_render_dict(self):
        dictionary = dict()
        for figure in Figure.objects.filter(game=self.game):
            pos = f"{'ABCDEFGH'[figure.width]}{figure.height + 1}"
            fig_dict = {'is_white': figure.is_white, 'role': figure.role}
            dictionary[pos] = fig_dict
        return dictionary

    def get_king(self, is_white: bool):
        for figure in Figure.objects.filter(game=self.game):
            if getattr(figure, 'role') == 'king' and getattr(figure, 'is_white') == is_white:
                return figure

    def get(self, height, width):
        try:
            return Figure.objects.get(height=height, width=width, game=self.game)
        except ObjectDoesNotExist:
            return
