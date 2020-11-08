import json
from django.contrib.auth import authenticate
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
# from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny
from rest_framework.status import (
    HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_200_OK
)
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from rest_registration import signals
from rest_registration.decorators import api_view_serializer_class_getter
from rest_registration.settings import registration_settings

from ..serializers import ChessUserSerializer, UserRegistrationSerializer, FigureSerializer, GameSerializer
from ..models import ChessUser, Figure, Game
from ..logic.manipulator import GameManipulator


# class CustomObtainAuthToken(ObtainAuthToken):
#     def post(self, request, *args, **kwargs):
#         response = super(CustomObtainAuthToken, self).post(request, *args, **kwargs)
#         token = Token.objects.get(key=response.data['token'])
#         return Response({'token': token.key, 'id': token.user_id})


# @permission_classes((AllowAny,))
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = ChessUser.objects.all().order_by('-date_joined')
    serializer_class = ChessUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'username'


# @permission_classes((AllowAny,))
class FigureViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    # queryset = Figure.objects.all()
    serializer_class = FigureSerializer

    def get_queryset(self, game_id=None):
        if game_id:
            figures = Figure.objects.filter(game__id=game_id)
        else:
            figures = Figure.objects.all()
        # print(games)
        return Response(self.serializer_class(figures, many=True).data)


class GameViewSet(viewsets.ModelViewSet):
    serializer_class = GameSerializer

    def get_queryset(self, search=None):
        if search:
            search = (Q(white_player=self.request.user) & Q(black_player__username__icontains=search)) | \
                     (Q(black_player=self.request.user) & Q(white_player__username__icontains=search))
        else:
            search = (Q(white_player=self.request.user) | Q(black_player=self.request.user))
        games = Game.objects.filter(Q(status__in='IST', test=False) & search).order_by('id')
        return Response(self.serializer_class(games, many=True).data)

    def list(self, request, users=None, games=None, **kwargs):
        self.object_list = self.get_queryset(games).data
        context = {'object_list': self.object_list}
        unfinished = self.get_queryset().data
        unfinished_game_users = [(game.get('black_player'), game.get('white_player')) for game in unfinished]
        unfinished_game_users = [dict(a) for b in unfinished_game_users for a in b]
        unfinished_game_user_ids = {user.get('id') for user in unfinished_game_users}
        search = Q(username__icontains=users) if users else Q()
        not_started_games_users = ChessUser.objects.filter(~Q(id__in=unfinished_game_user_ids) &
                                                           ~Q(id=self.request.user.id) & search).order_by('is_active')
        context['not_started_game_users'] = ChessUserSerializer(not_started_games_users, many=True).data
        return Response(context)

    def retrieve(self, request, pk, *args, **kwargs):
        # TODO Encapsulation
        game = Game.objects.get(id=pk)
        data = dict(self.serializer_class(game).data)
        data['render_dict'] = game.board.get_render_dict()
        return Response(data)

    def create(self, request, *args, **kwargs):
        data = json.loads(request.data)
        creator_is_white = data.get('creator_is_white')
        opponent_pk = data.get('opponent_pk')
        opponent = ChessUser.objects.get(pk=opponent_pk)
        try:
            game = GameManipulator.create(request.user, creator_is_white, opponent)
            data = {'detail': 'Game was created', 'game': GameSerializer(game).data}
        except ValueError:
            data = {'detail': 'This game already exists'}
        return Response(data=data)

    def partial_update(self, request, *args, **kwargs):
        data = json.loads(request.data)
        game = Game.objects.get(id=data['game_id'])
        if initiation := data.get('initiation'):
            if game.status == 'I':
                if initiation == 'False':
                    GameManipulator().decline(request.user, game)
                elif initiation == 'True':
                    GameManipulator().accept(request.user, game)
        elif reason := data.get('end_game'):
            GameManipulator().end_game(game, reason)
        return Response(data=data)


@api_view_serializer_class_getter(
    lambda: registration_settings.REGISTER_SERIALIZER_CLASS)
@api_view(['POST'])
@permission_classes(registration_settings.NOT_AUTHENTICATED_PERMISSION_CLASSES)
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user_serializer = ChessUserSerializer(data=serializer.data, context={'request': request})
    user_serializer.is_valid(raise_exception=True)

    kwargs = {}

    with transaction.atomic():
        user = user_serializer.save(**kwargs)

    signals.user_registered.send(sender=None, user=user, request=request)
    output_serializer_class = registration_settings.REGISTER_OUTPUT_SERIALIZER_CLASS  # noqa: E501
    output_serializer = output_serializer_class(
        instance=user,
        context={'request': request},
    )
    user_data = output_serializer.data
    return Response(user_data, status=status.HTTP_201_CREATED)


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
