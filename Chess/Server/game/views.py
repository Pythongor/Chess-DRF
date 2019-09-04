from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Q

from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN
from rest_framework import viewsets
from rest_framework.response import Response

from .models import Game, Figure
from .serializers import GameSerializer


class GameViewSet(viewsets.ViewSet):

    @staticmethod
    def list(request):
        queryset = Game.objects.filter(Q(white_player__id=request.user.id) &
                                       Q(white_player__id=request.user.id))
        serializer = GameSerializer(queryset, many=True)
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        queryset = Game.objects.all()
        game = get_object_or_404(queryset, pk=pk)
        if game.status == 'invited':
            return self.partial_update_invite(request, game)
        else:
            pass

    def partial_update_invite(self, request, game):
        if request.user == game.black_player:
            try:
                if request.data['invite'] == 'accept':
                    return self.start_game(request, game)
            except KeyError:
                pass
            return Response({'Error': 'invalid request'}, status=HTTP_400_BAD_REQUEST)
        elif request.user == game.white_player:
            return Response({'wait': 'game #{} wait for black player'.format(game.id)})
        else:
            return Response({'Error': 'it is not your game'}, status=HTTP_403_FORBIDDEN)

    def start_game(self, request, game):
        game_id = game.id
        self.create_figures(request, game)
        game = Game.objects.filter(id=game.id).update(status='started')
        return Response({'invite #{}'.format(game_id): 'started'})

    @staticmethod
    def create_figures(request, game):
        for i in enumerate(Figure.DEFAULT_FIGURES):
            status = 'START' if i[1] in ('rook', 'king') else 'NORMAL'
            Figure.objects.create(game=game, owner=game.white_player, is_white=True,
                                  role=i[1], status=status, height=1, width=i[0]+1)
            Figure.objects.create(game=game, owner=game.black_player, is_white=False,
                                  role=i[1], status=status, height=8, width=i[0]+1)
            Figure.objects.create(game=game, owner=game.white_player, is_white=True,
                                  role='pawn', status='NORMAL', height=2, width=i[0]+1)
            Figure.objects.create(game=game, owner=game.black_player, is_white=False,
                                  role='pawn', status='NORMAL', height=7, width=i[0]+1)

    @staticmethod
    def destroy(request, pk=None):
        queryset = Game.objects.all()
        game = get_object_or_404(queryset, pk=pk)
        if request.user in (game.black_player, game.white_player):
            game_id = game.id
            game.delete()
            return Response({'invite #{}'.format(game_id): 'denied'})
        else:
            return Response({'Error': 'it is not your game'}, status=HTTP_403_FORBIDDEN)

    def retrieve(self, request, pk=None):
        queryset = Game.objects.all()
        game = get_object_or_404(queryset, pk=pk)
        serializer = GameSerializer(game)
        context = serializer.data
        if context['status'] != 'invited':
            context['black figures'] = self.get_figures_data(game, False)
            context['white figures'] = self.get_figures_data(game, True)
        return Response(context)

    @staticmethod
    def get_figures_data(game, white):
        player = game.white_player if white else game.black_player
        figures = Figure.objects.filter(Q(owner=player) & Q(game=game))
        figures_data = []
        for figure in figures:
            figure_data = {"role": figure.role, "height": figure.height,
                           "width": figure.width, "status": figure.status}
            figures_data.append(figure_data)
        return figures_data

    def create(self, request):
        black_player = get_object_or_404(
            User, username=self.request.data.get('black_player')
        )
        game = Game.objects.create(white_player=request.user, black_player=black_player)
        return Response(
            {'white_player': game.black_player.username,
             'black_player': game.white_player.username,
             'status': game.status},
            status=HTTP_200_OK)
