import requests
import json
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, reverse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, ListView, View, DetailView
from django.utils.translation import gettext as _

# from ..models import ChessUser, Game, Figure
# from ..logic import Board
# from ..logic.manipulator import GameManipulator


class LoginMixin(View):
    def dispatch(self, request, *args, **kwargs):
        token = request.session.get('token')
        headers = {'Content-Type': 'application/json', 'Authorization': f'Token {token}'}
        request.headers = headers
        request.session.set_expiry(0)
        return super().dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class GamesView(ListView, LoginMixin):
    template_name = 'game/home.html'
    paginate_by = 3

    def get(self, request, *args, **kwargs):
        users = request.GET.get('users_search')
        games = request.GET.get('games_search')
        context = self.get_context_data(users, games)
        self.object_list = context['object_list']
        context['not_started_game_users'].sort(key=lambda x: not x['is_online'])
        # print(context['not_started_game_users'])
        context['not_started_game_users'] = self.paginate(
            context['not_started_game_users'], 2, 'not_started_game_users')
        return self.render_to_response(context)

    def get_context_data(self, users=None, games=None, **kwargs):
        url = 'http://127.0.0.1:8000/server/games/'
        data = {'users': users, 'games': games}
        response = requests.get(url=url, data=json.dumps(data), headers=self.request.headers)
        return response.json()

    def paginate(self, objects_list, per_page, object_name):
        paginator = Paginator(objects_list, per_page)
        page = self.request.GET.get(f'{object_name}_page', 1)
        try:
            objects = paginator.page(page)
        except PageNotAnInteger:
            objects = paginator.page(1)
        except EmptyPage:
            objects = paginator.page(paginator.num_pages)
        return objects

    def post(self, request, *args, **kwargs):
        users = request.POST.get('users', '')
        games = request.POST.get('games', '')
        return redirect(f'/client/home?users_search={users}&games_search={games}', users=users, games=games)


@method_decorator(login_required, name='dispatch')
class NewGameView(LoginMixin):
    game = None

    def post(self, request):
        creator_is_white = request.POST['creator_is_white'] in ('True', True)
        opponent_pk = int(request.POST['opponent_id'])
        url = 'http://127.0.0.1:8000/server/games/'
        data = {'creator_is_white': creator_is_white, 'opponent_pk': opponent_pk}
        response = requests.post(url=url, json=json.dumps(data), headers=self.request.headers)
        if 200 <= response.status_code < 300:
            pk = response.json().get('game')['id']
            return HttpResponseRedirect(f'game/{pk}')
        else:
            return HttpResponseRedirect(f'home')


@method_decorator(login_required, name='dispatch')
class GameView(DetailView, LoginMixin):
    object = None
    template_name = 'game/game.html'
    context_object_name = 'game'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        url = f'http://127.0.0.1:8000/server/games/{self.object["id"]}/'
        data = {**request.POST, 'game_id': self.object["id"]}
        requests.patch(url=url, json=json.dumps(data), headers=self.request.headers)
        return redirect(f'/client/game/{self.object["id"]}')

    def get_object(self, queryset=None):
        pk = self.kwargs.get('id')
        url = f'http://127.0.0.1:8000/server/games/{pk}'
        response = requests.get(url, headers=self.request.headers)
        return response.json()

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()
        context['row_options'] = tuple(map(lambda x: (str(x + 1), x), range(8)))
        context['column_options'] = tuple(map(lambda x: ('ABCDEFGH'[x], x), range(8)))
        context['transformation_figures'] = ('knight', 'bishop', 'rook', 'queen')
        if self.object['black_player']['id'] == request.user.id:
            context['rows'] = list(range(1, 9))
            context['columns'] = 'HGFEDCBA'
        elif self.object['white_player']['id'] == request.user.id:
            context['rows'] = list(range(8, 0, -1))
            context['columns'] = 'ABCDEFGH'
        return render(request, self.template_name, context)
