from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Game


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        write_only_fields = ('password',)

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class GameSerializer(serializers.ModelSerializer):
    white_player = serializers.CharField(read_only=True)
    black_player = serializers.CharField(read_only=True)

    class Meta:
        model = Game
        fields = ('id', 'white_player', 'black_player', 'status', 'white_message',
                  'black_message')
