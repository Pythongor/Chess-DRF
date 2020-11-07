from django.test.testcases import TestCase

from .mixins import ViewCaseMixin
from ..game_views import GamesView, NewGameView
from ...models import Game


class TestGames(TestCase, ViewCaseMixin):
    url = 'home'
    view_class = GamesView
    games = []

    def setup_class(self):
        super().setup_class(self)
        self.configure(self)
        self.games.append(Game.objects.create(status='I',
                                              white_player=self.white_player, black_player=self.black_player))
        self.games.append(Game.objects.create(status='D',
                                              white_player=self.white_player, black_player=self.black_player))
        self.games.append(Game.objects.create(status='S',
                                              white_player=self.test_player, black_player=self.black_player))

    def test_get_queryset(self):
        queryset = self.view.get_queryset()
        assert self.games[0] in queryset
        assert self.games[1] not in queryset
        assert self.games[2] not in queryset

    def test_get_context_data(self):
        context = self.view.get_context_data()
        assert len(context['not_started_game_users']) == 1
        assert context['not_started_game_users'][0].username == 'test'
        # assert len(context['unfinished_game_users']) == 1
        # assert context['unfinished_game_users'][0].username == 'test_black'
        assert len(context['object_list']) == 1
        assert context['object_list'][0] == self.games[0]


class TestNewGame(TestCase, ViewCaseMixin):
    url = 'new_game'
    view_class = NewGameView

    def test_post(self):
        data = {'opponent_id': self.black_player.id,
                'creator_is_white': True}
        self.configure(data)
        self.view.post(self.request)
        game = self.view.game
        assert game.black_player == self.black_player
        assert game.white_player == self.request.user
        assert game.status == 'I'
        assert not game.test
        assert game.white_message == 'Waiting for test_black...'
        assert game.black_message == 'Accept or decline test_white`s invite.'

    def test_post_1(self):
        data = {'opponent_id': self.test_player.id,
                'creator_is_white': False}
        self.configure(data)
        self.view.post(self.request)
        game = self.view.game
        assert game.black_player == self.request.user
        assert game.white_player == self.test_player
        assert game.status == 'I'
        assert not game.test
        assert game.white_message == 'Accept or decline test_white`s invite.'
        assert game.black_message == 'Waiting for test...'
