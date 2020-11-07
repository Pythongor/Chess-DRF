from server.models import Figure, Game, ChessUser


class ChessCaseMixin:
    white_player = None
    black_player = None

    def setup_class(self):
        self.white_player = ChessUser.objects.create_user('test_white')
        self.black_player = ChessUser.objects.create_user('test_black')

    def teardown_class(self):
        for model in (ChessUser, Figure, Game):
            model.objects.all().delete()
