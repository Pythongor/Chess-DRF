from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, reverse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, ListView, View, DetailView
from django.utils.translation import gettext as _

from ..models import ChessUser, Game, Figure
from ..logic import Board
from ..logic.manipulator import GameManipulator


@method_decorator(login_required, name='dispatch')
class GamesView(ListView):
    model = Game
    template_name = 'game/home.html'
    paginate_by = 3

    def get(self, request, *args, **kwargs):
        users = request.GET.get('users_search')
        games = request.GET.get('games_search')
        self.object_list = self.get_queryset(games)
        print(users, games, request.POST, request.GET)
        context = self.get_context_data(users, games)
        return self.render_to_response(context)

    def get_queryset(self, search=None):
        if search:
            search = (Q(white_player=self.request.user) & Q(black_player__username__icontains=search)) | \
                     (Q(black_player=self.request.user) & Q(white_player__username__icontains=search))
        else:
            search = (Q(white_player=self.request.user) | Q(black_player=self.request.user))
        return Game.objects.filter(Q(status__in='IST', test=False) & search).order_by('id')

    def get_context_data(self, users=None, games=None, **kwargs):
        self.object_list = self.get_queryset(games)
        context = super().get_context_data(**kwargs)
        unfinished = self.get_queryset()
        unfinished_game_users = [(game.black_player, game.white_player) for game in unfinished]
        unfinished_game_users = [a for b in unfinished_game_users for a in b]
        unfinished_game_user_ids = {user.id for user in unfinished_game_users}
        search = Q(username__icontains=users) if users else Q()
        not_started_games_users = ChessUser.objects.filter(~Q(id__in=unfinished_game_user_ids) &
                                                           ~Q(id=self.request.user.id) & search).order_by('is_active')
        context['not_started_game_users'] = self.paginate(not_started_games_users, 2, 'not_started_game_users')
        return context

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
        return redirect(f'/home?users_search={users}&games_search={games}', users=users, games=games)


@method_decorator(login_required, name='dispatch')
class NewGameView(View):
    game = None

    def post(self, request):
        creator_is_white = request.POST['creator_is_white'] in ('True', True)
        opponent_id = int(request.POST['opponent_id'])
        opponent = ChessUser.objects.get(id=opponent_id)
        self.game = GameManipulator.create(request.user, creator_is_white, opponent)
        return HttpResponseRedirect(f'game/{self.game.id}')


@method_decorator(login_required, name='dispatch')
class GameView(DetailView):
    model = Game
    template_name = 'game/game.html'
    object = None
    context_object_name = 'game'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.POST.get('initiation'):
            return self._game_init(request)
        elif request.POST.get('end_game'):
            return self._finish_game(request)
        elif request.POST.get('transformation'):
            return self._transform(request)
        elif request.POST.get('start_column'):
            return self._turn(request)
        return redirect(f'/game/{self.object.id}')

    def _game_init(self, request):
        initiation = request.POST.get('initiation')
        if initiation == 'True':
            GameManipulator().accept(request.user, self.object)
            return redirect(f'/game/{self.object.id}')
        elif initiation == 'False':
            GameManipulator().decline(request.user, self.object)
            return redirect('/home')

    def _finish_game(self, request):
        reason = request.POST.get('end_game')
        GameManipulator().end_game(self.object, reason)
        return redirect(f'/game/{self.object.id}')

    def _transform(self, request):
        role = request.POST.get('transformation')
        GameManipulator().turn(request.user, self.object, role=role)
        return redirect(f'/game/{self.object.id}')

    def _turn(self, request):
        start_row = request.POST.get('start_row')
        start_column = request.POST.get('start_column')
        end_row = request.POST.get('end_row')
        end_column = request.POST.get('end_column')
        start = (int(start_row), int(start_column))
        end = (int(end_row), int(end_column))
        GameManipulator().turn(request.user, self.object, start, end)
        return redirect(f'/game/{self.object.id}')

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()
        context['row_options'] = tuple(map(lambda x: (str(x + 1), x), range(8)))
        context['column_options'] = tuple(map(lambda x: ('ABCDEFGH'[x], x), range(8)))
        context['transformation_figures'] = ('knight', 'bishop', 'rook', 'queen')
        if type(self.object.board) == Board:
            context['render_dict'] = self.object.board.get_render_dict()
            if self.object.black_player == request.user:
                context['rows'] = list(range(1, 9))
                context['columns'] = 'HGFEDCBA'
            elif self.object.white_player == request.user:
                context['rows'] = list(range(8, 0, -1))
                context['columns'] = 'ABCDEFGH'
        # print(context['render_dict'])
        return render(request, self.template_name, context)

# TODO adaptive design
# TODO: AJAX
# TODO: DRF
# TODO: python anywhere
