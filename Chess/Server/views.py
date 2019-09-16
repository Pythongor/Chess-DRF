from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token

from rest_framework import viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.status import (
    HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_200_OK, HTTP_403_FORBIDDEN
)

from .models import Game, Figure
from .serializers import GameSerializer
from .game_checker import GameChecker
from .game_manipulator import GameManipulator
from .serializers import UserSerializer


class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super(CustomObtainAuthToken, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        return Response({'token': token.key, 'id': token.user_id})


class GameViewSet(viewsets.ViewSet):

    @staticmethod
    def list(request):
        queryset = Game.objects.filter(Q(white_player__id=request.user.id) |
                                       Q(black_player__id=request.user.id))
        serializer = GameSerializer(queryset, many=True)
        return Response({'games': serializer.data})

    def partial_update(self, request, pk=None):
        queryset = Game.objects.all()
        game = get_object_or_404(queryset, pk=pk)
        if game.status == 'INVITED':
            return self.partial_update_invite(request, game)
        elif game.status == 'STARTED':
            return self.partial_update_move(request, game)
        else:
            pass

    def partial_update_invite(self, request, game):
        if request.user == game.black_player:
            try:
                if request.data['invite'] == 'accept':
                    return self.start_game(game)
            except KeyError:
                pass
            return Response({'Error': 'invalid request'}, status=HTTP_400_BAD_REQUEST)
        elif request.user == game.white_player:
            return Response({'Wait': 'game #{} wait for black player'.format(game.id)})
        else:
            return Response({'Error': 'it is not your game'},
                            status=HTTP_403_FORBIDDEN)

    @staticmethod
    def start_game(game):
        manipulator = GameManipulator(game)
        manipulator.start()
        return Response({'invite #{}'.format(game.id): 'started'})

    def partial_update_move(self, request, game):
        player = {True: game.white_player, False: game.black_player}[game.white_turn]
        if request.user.username != str(player):
            data = {'ERROR MESSAGE': 'Wait your turn!'}
        else:
            checker = GameChecker(game)
            data = checker.patch_request(request.data['turn'])
            if any(['ERROR MESSAGE', 'GAME']) not in data:
                self.make_move(game, data)
        return Response(data)

    @staticmethod
    def make_move(game, command):
        manipulator = GameManipulator(game)
        manipulator.make_move(command)

    @staticmethod
    def destroy(request, pk=None):
        queryset = Game.objects.all()
        game = get_object_or_404(queryset, pk=pk)
        if request.user in (game.black_player, game.white_player):
            game_id = game.id
            game.delete()
            return Response({'invite #{}'.format(game_id): 'denied'})
        else:
            return Response({'Error': 'it is not your game'},
                            status=HTTP_403_FORBIDDEN)

    def retrieve(self, request, pk=None):
        queryset = Game.objects.all()
        game = get_object_or_404(queryset, pk=pk)
        serializer = GameSerializer(game)
        context = serializer.data
        if context['status'] != 'INVITED':
            context['black_figures'] = self.get_figures_data(game, False)
            context['white_figures'] = self.get_figures_data(game, True)
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

    @staticmethod
    def create(request):
        black_player = get_object_or_404(
            User, username=request.data.get('black_player')
        )
        game = Game.objects.create(white_player=request.user,
                                   black_player=black_player)
        return Response(
            {
                'id': game.id,
                'white_player': game.black_player.username,
                'black_player': game.white_player.username,
                'status': game.status},
            status=HTTP_200_OK)


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    if username is None or password is None:
        return Response({'error': 'Please provide both username and password'},
                        status=HTTP_400_BAD_REQUEST)
    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'Invalid Credentials'},
                        status=HTTP_404_NOT_FOUND)
    token, _ = Token.objects.get_or_create(user=user)
    print(get_token(request))
    return Response({'token': token.key},
                    status=HTTP_200_OK)


class UserView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, pk=None):
        if pk:
            user = User.objects.get(pk=pk)
            serializer = UserSerializer(data=user)
            return Response(serializer.data)
        else:
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            return Response({"users": serializer.data})

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            login_user = auth_login(request, user)
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"username": request.data['username'],
                             "email": request.data['email'],
                             "password": request.data['password'],
                             "token": token.key})
        else:
            return Response({"error": "Invalid Credentials"})


