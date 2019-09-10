from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Q
from django.urls import path

from rest_framework.authtoken.models import Token

import requests


def tokenize_headers(request, headers=None):
    headers = {} if headers is None else headers
    token, _ = Token.objects.get_or_create(user=request.user)
    headers['Authorization'] = 'Token {}'.format(token)
    return headers


class GameListView(TemplateView):
    template_name = 'client/games.html'

    def get(self, request, *a, **kw):
        context = requests.get('http://127.0.0.1:8000/server/games',
                               headers=tokenize_headers(request))
        return self.render_to_response(context.json())


class GameView(TemplateView):
    template_name = 'client/game.html'

    def get(self, request, pk=None, *a, **kw):
        context = requests.get(
            'http://127.0.0.1:8000/server/games/{}'.format(pk),
            headers=tokenize_headers(request))
        context = context.json()
        context['height'] = list(zip([i % 2 for i in range(8, 0, -1)],
                                     list(range(8, 0, -1))))
        context['width'] = list(zip([i % 2 for i in range(1, 9)],
                                    [i for i in range(1, 9)], 'abcdefgh'))
        context = self.figure_dict_refactoring(context, True)
        context = self.figure_dict_refactoring(context, False)
        return self.render_to_response(context)

    @staticmethod
    def figure_dict_refactoring(context, white):
        color = 'white' if white else 'black'
        figures = []
        for figure in context[color + '_figures']:
            figures.append([figure['height'], figure['width'],
                            figure['role']])
        context[color + '_figures'] = figures
        return context

    # @staticmethod
    # def tokenize_headers(headers):
    #     token =
