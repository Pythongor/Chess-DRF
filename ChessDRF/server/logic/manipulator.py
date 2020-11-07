from django.db.models import Q, F
from ..models import Game, Figure


class GameManipulator:
    messages = {
        'INF': 'There is no figure!',
        'IFF': 'This figure is`nt yours!',
        'IM': 'Illegal move!',
        'IC': 'Check your king!',
        'T': 'Select figure role to transform.',
    }

    @staticmethod
    def create(user, creator_is_white, opponent):
        if creator_is_white:
            white_player = user
            black_player = opponent
            white_message = f'Waiting for {black_player.username}...'
            black_message = f'Accept or decline {white_player.username}`s invite.'
        elif not creator_is_white:
            white_player = opponent
            black_player = user
            white_message = f'Accept or decline {black_player.username}`s invite.'
            black_message = f'Waiting for {white_player.username}...'
        else:
            raise AttributeError('"creator_is_white" must be True or False.')
        if Game.objects.filter(Q(white_player=white_player, black_player=black_player, status__in='SI')):
            raise ValueError('This game already exists')
        game = Game.objects.create(white_player=white_player, black_player=black_player,
                                   white_message=white_message, black_message=black_message)
        return game

    @staticmethod
    def correct_user(user, game):
        if user in (game.white_player, game.black_player):
            return True

    def check_initialize(self, user, game):
        if not self.correct_user(user, game):
            raise ValueError('Incorrect user!')
        if getattr(game, 'status') == 'I':
            black_is_creator = 'Accept or decline' in getattr(game, 'white_message')
            white_is_creator = 'Accept or decline' in getattr(game, 'black_message')
            if not black_is_creator ^ white_is_creator:
                raise ValueError('Game has incorrect messages')
            user_is_white = user == game.white_player
            if (black_is_creator and user_is_white) or (white_is_creator and not user_is_white):
                return True
            else:
                raise ValueError('You can`t do that!')
        else:
            raise ValueError('Game is not in initialize mode')

    def accept(self, user, game):
        if self.check_initialize(user, game):
            game.status = 'S'
            game.black_message = f'{game.white_player.username} turn. Please wait.'
            game.white_message = 'Your turn.'
            game.white_turn = True
            game.save()
            game.board.initialize()

    def decline(self, user, game):
        if self.check_initialize(user, game):
            game.status = 'R'
            game.save()

    def turn(self, user, game, start=None, end=None, role=None):
        if not self.correct_user(user, game):
            raise ValueError('Incorrect user!')
        if game.status in 'TS':
            # print(user, game, start, end, role)
            status = game.turn(start, end, role)
            self._change_messages(user, game, status)
            game.save()
            self.check_end_of_game(game)
            return status

    def _change_messages(self, user, game, status):
        user_is_white = user == game.white_player
        if message := self.messages.get(status):
            if user_is_white:
                game.white_message = message
            else:
                game.black_message = message
        else:
            if user_is_white:
                game.white_message = f'Waiting for {game.black_player.username}...'
                game.black_message = 'Your turn.'
            else:
                game.black_message = f'Waiting for {game.white_player.username}...'
                game.white_message = 'Your turn.'

    def check_end_of_game(self, game):
        if status := game.checker.check_end_of_game():
            if 'M' in status:
                self.end_game(game, status)
            else:
                raise ValueError('Illegal status of end game!')

    def end_game(self, game, reason):
        reasons = {
            'SM': (self._draw, 'no possible moves.'),
            'IM': (self._draw, 'both players have insufficient pieces to win.'),
            'M': (self._mate, ),
        }
        reasons[reason][0](game, *reasons[reason][1:])
        game.white_player.games_played = game.white_player.games_played + 1
        game.white_player.save()
        game.black_player.games_played = game.black_player.games_played + 1
        game.black_player.save()
        game.save()

    @staticmethod
    def _draw(game, reason):
        game.status = 'D'
        game.white_message = game.black_message = f'Draw. Reason: {reason}'
        game.white_player.games_tied = game.white_player.games_tied + 1
        game.black_player.games_tied = game.black_player.games_tied + 1

    @staticmethod
    def _mate(game):
        if game.white_turn:
            winner, loser = game.black_player, game.white_player
            game.status = 'B'
            game.white_message = 'Sorry, you lose :( Lucky next time!'
            game.black_message = 'Congratulations! You win!'
        else:
            winner, loser = game.white_player, game.black_player
            game.status = 'W'
            game.white_message = 'Congratulations! You win!'
            game.black_message = 'Sorry, you lose :( Better luck next time!'
        winner.games_won = winner.games_won + 1
        loser.games_lost = loser.games_lost + 1


