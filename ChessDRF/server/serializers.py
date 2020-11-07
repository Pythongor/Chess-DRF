from os import listdir
from random import choice
from django.conf import settings
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import Game, Figure, ChessUser


class ChessUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password', 'placeholder': 'Password'}
    )

    class Meta:
        model = ChessUser
        fields = '__all__'
        read_only_fields = ['photo']
        write_only_fields = ('password', )

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        chess_user = super().create(validated_data)
        figure = choice(listdir(f'{settings.STATIC_ROOT}/figures'))
        chess_user.photo = f'/figures/{figure}'
        chess_user.save()
        return chess_user


class UserRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(
        # write_only=True,
        required=True,
        style={'input_type': 'password', 'placeholder': 'Password'}
    )
    confirm_password = serializers.CharField(
        # write_only=True,
        required=True,
        style={'input_type': 'password', 'placeholder': 'Password confirmation'}
    )

    def validate(self, data):
        if not data.get('password') or not data.get('confirm_password'):
            raise serializers.ValidationError("Please enter a password and "
                                              "confirm it.")

        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError("Those passwords don't match.")

        return data


class GameSerializer(serializers.ModelSerializer):
    black_player = ChessUserSerializer(read_only=True)
    white_player = ChessUserSerializer(read_only=True)

    class Meta:
        model = Game
        fields = '__all__'


class FigureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Figure
        fields = '__all__'
