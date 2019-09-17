from .models import Figure, Game
from .game_checker import GameChecker


class GameManipulator:
    def __init__(self, game):
        self.game = game
        self.checker = GameChecker(game)

    def start(self, create=True):
        if create:
            self._create_figures()
        self.game.status = 'STARTED'
        self.game.white_message = 'Your turn'
        self.game.white_turn = True
        self.game.black_message = 'Wait your turn'
        self.game.save()

    def _switch_players(self):
        if not self.game.white_turn:
            self.game.white_message = 'Your turn'
            self.game.black_message = 'Wait your turn'
        elif self.game.white_turn:
            self.game.black_message = 'Your turn'
            self.game.white_message = 'Wait your turn'
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

    def next_turn_modeling(self, command):
        virtual = Game.objects.create(
            status='VIRTUAL', white_player=self.game.white_player,
            black_player=self.game.black_player, white_turn=self.game.white_turn)
        virtual_checker = GameChecker(virtual)
        virtual_manipulator = GameManipulator(virtual)
        figures = Figure.objects.filter(game=self.game)
        for figure in figures:
            Figure.objects.create(game=virtual, owner=figure.owner,
                                  is_white=figure.is_white, role=figure.role,
                                  status=figure.status, height=figure.height,
                                  width=figure.width)
        virtual_manipulator.make_move(command)
        response = virtual_checker.check_checkup()
        virtual.delete()
        for figure in Figure.objects.filter(game=virtual):
            figure.delete()
        return response

    def make_move(self, command):
        actions = {
            'ERROR MESSAGE': self._change_message,
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
                response = actions[i](command[i])
                self._reset_en_passants()
                return response

    def _change_message(self, command):
        if self.game.white_turn:
            self.game.white_message = command['ERROR MESSAGE']
        else:
            self.game.black_message = 'Illegal move'
        self.game.save()

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
        # print(turn)
        modes = {'0': [[1, 1], [1, 4]],
                 '1': [[1, 8], [1, 6]],
                 '2': [[8, 1], [8, 4]],
                 '3': [[8, 8], [8, 6]]}
        positions = modes[turn[1]]
        self._move_figure_status(positions)
        self._move_figure_status(turn[0])

    def _en_passant(self, turn):
        attacked = self.checker.get_figure(turn[1])
        attacked.delete()
        attacker = self.checker.get_figure(turn[0], False)
        attacker.update(height=turn[2][0], width=turn[2][1])

    def _reset_en_passants(self):
        en_passants = Figure.objects.filter(game=self.game, status='EN PASSANT',
                                            is_white=not self.game.white_turn)
        for i in en_passants:
            i.status = 'NORMAL'
            i.save()
