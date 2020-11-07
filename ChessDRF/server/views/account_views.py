from os import listdir
from random import choice
from django.conf import settings
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView, DetailView
from django.views.generic.edit import FormView

from ..forms import ImageForm, ChessUserCreationForm
from ..models import ChessUser


class EnterView(TemplateView):
    template_name = 'accounts/enter.html'


class SignInView(LoginView):
    template_name = 'accounts/login.html'

    def get_success_url(self):
        username = self.get_form_kwargs()['data'].get('username')
        return 'users/' + username


class SignUpView(FormView):
    template_name = 'accounts/sign_up.html'
    form_class = ChessUserCreationForm
    user = None

    def form_valid(self, form):
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            self.user = authenticate(username=username, password=password)
            figure = choice(listdir(f'{settings.STATIC_ROOT}/figures'))
            self.user.photo = f'/figures/{figure}'
            self.user.save()
            login(self.request, self.user)
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)

    def get_success_url(self):
        return f'users/{self.user}'


class UserView(DetailView):
    model = ChessUser
    template_name = 'accounts/profile.html'

    def get_object(self, queryset=None):
        return get_object_or_404(ChessUser, username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ImageForm()
        return context
