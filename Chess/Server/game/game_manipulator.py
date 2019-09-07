from .models import Figure, Game


class GameManipulator:
    def __init__(self, game):
        self.game = game

    def start(self):
        self.create_figures()
        db_game = Game.objects.filter(id=self.game.id)
        db_game.update(status='STARTED', white_message='Your turn',
                       white_turn=True, black_message='Wait your turn')

    def create_figures(self):
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
