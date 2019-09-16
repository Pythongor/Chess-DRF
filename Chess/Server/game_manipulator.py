from .models import Figure, Game
from .game_checker import GameChecker


class GameManipulator:
    def __init__(self, game):
        self.game = game
        self.checker = GameChecker(game)

    def start(self):
        self._create_figures()
        self.game.status = 'STARTED'
        self.game.white_message = 'Your turn'
        self.game.white_turn = True
        self.game.black_message = 'Wait your turn'
        self.game.save()

    def _switch_players(self):
        self.game.white_message, self.game.black_message = self.game.black_message, \
                                                           self.game.white_message
        self.game.white_turn = not self.game.white_turn
        self.game.save()

    def _create_figures(self):
        for i in enumerate(Figure.DEFAULT_FIGURES):
            status = 'START' if i[1] in ('rook', 'king') else 'NORMAL'
            Figure.objects.create(game=self.game, owner=self.game.white_player, is_white=True,
                                  role=i[1], status=status, height=1, width=i[0] + 1)
            Figure.objects.create(game=self.game, owner=self.game.black_player, is_white=False,
                                  role=i[1], status=status, height=8, width=i[0] + 1)
            Figure.objects.create(game=self.game, owner=self.game.white_player, is_white=True,
                                  role='pawn', status='NORMAL', height=2, width=i[0] + 1)
            Figure.objects.create(game=self.game, owner=self.game.black_player, is_white=False,
                                  role='pawn', status='NORMAL', height=7, width=i[0] + 1)

    def make_move(self, command):
        actions = {
            'MOVE ACCEPT': self._move_figure,
            'MOVE ACCEPT STATUS': self._move_figure_status,
            'ATTACK ACCEPT': self._attack_figure,
            'ATTACK ACCEPT STATUS': self._attack_figure_status,
            'CASTLING ACCEPT': self._castling,
            'ACCEPT EN PASSANT': self._en_passant,
            'MOVE TRANSFORMATION': self._move_transformation,
            'ATTACK TRANSFORMATION': self._attack_transformation,
        }
        for i in actions:
            if i in command:
                self._switch_players()
                return actions[i](command[i])

    def _move_figure(self, turn):
        figure = self.checker.get_figure(turn[0], False)
        figure.update(height=turn[1][0], width=turn[1][1])

    def _move_figure_status(self, turn):
        self._move_figure(turn)
        figure = self.checker.get_figure(turn[1], False)
        self._change_status(figure)

    @staticmethod
    def _change_status(figure):
        statuses = {
            ('pawn', 'NORMAL'): 'EN PASSANT',
            ('pawn', 'EN PASSANT'): 'NORMAL',
            ('king', 'START'): 'NORMAL',
            ('rook', 'START'): 'NORMAL',
        }
        figure.update(status=statuses[(figure[0].role, figure[0].status)])

    def _attack_figure(self, turn):
        attacked = self.checker.get_figure(turn[1], False)
        attacked.delete()
        attacker = self.checker.get_figure(turn[0], False)
        attacker.update(height=turn[1][0], width=turn[1][1])

    def _attack_figure_status(self, turn):
        self._attack_figure(turn)
        figure = self.checker.get_figure(turn[1], False)
        self._change_status(figure)

    def _move_transformation(self, turn):
        pawn = self.checker.get_figure(turn[0], False)
        pawn.update(height=turn[1][0], width=turn[1][1], role='queen')

    def _attack_transformation(self, turn, status):
        attacked = self.checker.get_figure(turn[1], False)
        attacked.delete()
        self._move_transformation(turn)

    def _castling(self, turn):
        modes = {'0': [[1, 1], [1, 4]],
                 '1': [[1, 8], [1, 6]],
                 '2': [[8, 1], [8, 4]],
                 '3': [[8, 8], [8, 6]]}
        positions = modes[turn[1]]
        self._move_figure_status(positions)
        self._move_figure_status(turn[0])

    def _en_passant(self, turn):
        attacked = self.checker.get_figure(turn[1], False)
        attacked.delete()
        attacker = self.checker.get_figure(turn[0], False)
        attacker.update(height=turn[2][0], width=turn[2][1])
