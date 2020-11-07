from django.test import RequestFactory

from server.models import Figure, Game, ChessUser


class ViewCaseMixin:
    black_player = None
    white_player = None
    test_player = None
    client = None
    factory = None
    url = None
    view_class = None
    view = None
    request = None
    kwargs = dict()

    def setup_class(self):
        self.white_player = ChessUser.objects.create_user('test_white')
        self.black_player = ChessUser.objects.create_user('test_black')
        self.test_player = ChessUser.objects.create_user('test')
        self.factory = RequestFactory()
        self.request = self.factory.get(self.url)
        self.request.user = self.white_player
        self.view = self.setup_view(self.view_class, self.request, **self.kwargs)

    def teardown_class(self):
        for model in (ChessUser, Figure, Game):
            model.objects.all().delete()

    @staticmethod
    def setup_view(view_cls, request, *args, **kwargs):
        view = view_cls()
        view.request = request
        view.args = args
        view.kwargs = kwargs
        return view

    def configure(self, data=None):
        if data:
            self.request = self.factory.post(self.url, data)
        else:
            self.request = self.factory.get(self.url)
        self.request.user = self.white_player
        self.view = self.setup_view(self.view_class, self.request, **self.kwargs)
