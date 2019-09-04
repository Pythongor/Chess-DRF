from rest_framework import serializers

from .models import Game, Figure


class GameSerializer(serializers.ModelSerializer):
    white_player = serializers.CharField(read_only=True)
    black_player = serializers.CharField(read_only=True)

    class Meta:
        model = Game
        fields = ('id', 'white_player', 'black_player', 'status')
