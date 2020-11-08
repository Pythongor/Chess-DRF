import requests
from django.shortcuts import redirect, render
from django.contrib.auth import login, get_user_model
from django.views.generic import View, FormView, TemplateView
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from ..forms import LoginForm, SignUpForm

server_root = f'http://127.0.0.1:8000/server'


class Deserialized(object):
    def __init__(self, dictionary):
        for key in dictionary:
            setattr(self, key, dictionary[key])


class LoginMixin(View):
    def dispatch(self, request, *args, **kwargs):
        token = request.session.get('token')
        headers = {'Content-Type': 'application/json', 'Authorization': f'Token {token}'}
        request.headers = headers
        request.session.set_expiry(0)
        return super().dispatch(request, *args, **kwargs)


class EnterView(TemplateView):
    template_name = 'accounts/enter.html'


class LoginView(FormView):
    template_name = 'accounts/login.html'
    form_class = LoginForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            data = {'login': username, 'password': password}
            url = f'{server_root}/accounts/login/'
            response = requests.post(url=url, json=data, headers={'Accept': 'application/json'})
            dct = response.json()
            login(request, get_user_model().objects.get(username=username))
            request.session['token'] = dct.get('token')
            return redirect(f'http://127.0.0.1:8000/client/users/{username}')
        else:
            return render(request, self.template_name, {'form': form})


class SignUpView(FormView):
    form_class = SignUpForm
    template_name = 'accounts/sign_up.html'

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            confirm_password = form.cleaned_data.get('confirm_password')
            data = {'login': username, 'username': username, 'password': password, 'confirm_password': confirm_password}
            url = f'{server_root}/accounts/register/'
            login_url = f'{server_root}/accounts/login/'
            headers = {'Accept': 'application/json'}
            requests.post(url=url, json=data, headers=headers)
            login_response = requests.post(url=login_url, json=data, headers=headers)
            login_dct = login_response.json()
            login(request, get_user_model().objects.get(username=username))
            request.session['token'] = login_dct.get('token')
            return redirect(f'http://127.0.0.1:8000/client/users/{username}')
        else:
            return render(request, self.template_name, {'form': form})


class ProfileView(TemplateView, LoginMixin, LoginRequiredMixin):
    template_name = 'accounts/profile.html'

    def get(self, request, *args, **kwargs):
        context = {}
        username = kwargs['username']
        url = f'http://127.0.0.1:8000/server/users/{username}/'
        response = requests.get(url=url, headers=request.headers)
        if response.status_code == 200:
            context['user'] = Deserialized(response.json())
        elif response.status_code == 401:
            return redirect(settings.LOGIN_URL)
        return self.render_to_response(context)

