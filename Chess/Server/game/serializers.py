from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.status import HTTP_200_OK

from rest_framework import serializers, viewsets
from rest_framework.response import Response

from .models import Game, Figure


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')
        write_only_fields = ('password',)


class GameSerializer(serializers.ModelSerializer):
    white_player = serializers.CharField(read_only=True)
    black_player = serializers.CharField(read_only=True)

    class Meta:
        model = Game
        fields = ('id', 'white_player', 'black_player', 'status')


class GameViewSet(viewsets.ViewSet):

    def list(self, request):
        queryset = Game.objects.all()
        serializer = GameSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Game.objects.all()
        game = get_object_or_404(queryset, pk=pk)
        serializer = GameSerializer(game)
        return Response(serializer.data)

    def create(self, request):
        black_player = get_object_or_404(
            User, username=self.request.data.get('black_player')
        )
        game = Game.objects.create(white_player=request.user, black_player=black_player)
        return Response(
            {'white_player': game.black_player.username,
             'black_player': game.white_player.username,
             'status': game.status
             },
            status=HTTP_200_OK)
