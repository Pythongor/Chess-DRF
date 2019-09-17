from django.shortcuts import redirect, render, reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.core.paginator import Paginator
from django.views.generic import TemplateView, FormView
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from rest_framework.authtoken.models import Token

import requests

from .forms import PlayerMoveForm


def nothing(request, url, pk):
    return redirect('/client/'+url+'/'+str(pk))


def tokenize_headers(request, headers=None):
    headers = {} if headers is None else headers
    token, _ = Token.objects.get_or_create(user=request.user)
    headers['Authorization'] = 'Token {}'.format(token)
    headers['Content-Type'] = 'application/json'
    return headers


def registration(request):
    context = {}
    form = UserCreationForm()
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            new_user = User.objects.create_user(username=username,
                                                password=password)
            login(request, authenticate(username=username, password=password))
            return redirect('games')
    context['user_form'] = form
    return render(request, 'client/registration.html', context)


class InvitedGame(TemplateView):
    template_name = 'client/invited_game.html'

    def get(self, request, pk=None, *a, **kw):
        print('GET')
        context = self.requests_get(request, pk)
        return self.render_to_response(context.json())

    def requests_get(self, request, pk):
        context = requests.get(
            'http://127.0.0.1:8000/server/games/{}'.format(pk),
            headers=tokenize_headers(request))
        context = context.json()
        return context


class GameListView(TemplateView):
    template_name = 'client/games.html'

    def get(self, request, *a, **kw):
        context = requests.get('http://127.0.0.1:8000/server/games',
                               headers=tokenize_headers(request)).json()
        paginator = Paginator(context['games'], 2)
        page = request.GET.get('page')
        games = paginator.get_page(page)
        users = requests.get(
            'http://127.0.0.1:8000/server/users',
            headers=tokenize_headers(request)).json()['users']
        return self.render_to_response({'games': games, 'users': users})


def invite(request, username):
    data = {'black_player': username}
    response = requests.post('http://127.0.0.1:8000/server/games/',
                             json=data, headers=tokenize_headers(request))
    print(response.json())
    game_id = response.json()['id']
    return redirect('../{}?0'.format(game_id))


def accept_invite(request, pk):
    data = {'invite': 'accept'}
    response = requests.patch(
        'http://127.0.0.1:8000/server/games/{}/'.format(pk),
        json=data, headers=tokenize_headers(request))
    return redirect('../{}'.format(pk))


def delete(request, pk):
    requests.delete('http://127.0.0.1:8000/server/games/{}/'.format(pk),
                    headers=tokenize_headers(request))
    return redirect('..')


class GameView(FormView):
    template_name = 'client/game.html'
    form_class = PlayerMoveForm

    def get(self, request, pk=None, *a, **kw):
        context = self.requests_get(request, pk)
        return self.render_to_response(context)

    def requests_get(self, request, pk):
        context = requests.get(
            'http://127.0.0.1:8000/server/games/{}'.format(pk),
            headers=tokenize_headers(request))
        context = context.json()
        if context['status'] == 'INVITED':
            self.success_url = 'invite/{}'.format(context['id'])
        else:
            self.success_url = str(pk)
            context = self._figure_dict_refactoring(context, True)
            context = self._figure_dict_refactoring(context, False)
        self._add_representation_content(request, context)
        return context

    @staticmethod
    def _figure_dict_refactoring(context, white):
        color = 'white' if white else 'black'
        figures = []
        # statuses = []
        for figure in context[color + '_figures']:
            figures.append([figure['height'], figure['width'],
                            figure['role']])
            # statuses.append(figure['status'])
        context[color + '_figures'] = figures
        # context['statuses'] = statuses
        return context

    def _add_representation_content(self, request, context):
        if str(request.user.username) == context['white_player']:
            context['height'] = list(zip([i % 2 for i in range(8, 0, -1)],
                                         list(range(8, 0, -1))))
        elif str(request.user.username) == context['black_player']:
            context['height'] = list(zip([i % 2 for i in range(1, 9)],
                                         list(range(1, 9))))
        context['width'] = list(zip([i % 2 for i in range(1, 9)],
                                    [i for i in range(1, 9)], 'ABCDEFGH'))
        context['form'] = self.form_class()

    def post(self, request, pk=None, *args, **kwargs):
        self.success_url = str(pk)
        form = self.form_class(request.POST)
        context = self.requests_get(request, pk)
        if form.is_valid():
            return self._patch(request, pk, form)
        else:
            context['form'] = form
            context = self._change_message(request, context,
                                           'Illegal move. Try again')
            return self.render_to_response(context)

    def _patch(self, request, pk, form):
        response = self.make_turn_request(request, pk, form)
        context = self.requests_get(request, pk)
        context['response'] = response.json()
        if 'GAME END' in response.json():
            self._game_end(request, response)
        elif 'ERROR MESSAGE' in response.json():
            self._change_message(request, context,
                                 response.json()['ERROR MESSAGE'])
        else:
            pass
        return HttpResponseRedirect(reverse(
            "nothing", args=['games', str(pk)]))

    @staticmethod
    def make_turn_request(request, pk, form):
        width = 'abcdefgh'
        start_point = list(form.cleaned_data['start'])
        start_point = [int(start_point[1]),
                       width.index(start_point[0].lower()) + 1]
        end_point = list(form.cleaned_data['end'])
        end_point = [int(end_point[1]),
                     width.index(end_point[0].lower()) + 1]
        data = {"turn": [start_point, end_point]}
        response = requests.patch(
            'http://127.0.0.1:8000/server/games/{}/'.format(pk),
            json=data, headers=tokenize_headers(request))
        return response

    def _game_end(self, request, response):
        pass

    @staticmethod
    def _change_message(request, context, message):
        if request.user.username == context['white_player']:
            context['white_message'] = message
        elif request.user.username == context['black_player']:
            context['black_message'] = message
        return context
