import requests
from django import forms
from django.forms.utils import ErrorList


class PErrorList(ErrorList):
    def __str__(self):
        return self.as_p()

    def as_p(self):
        if not self:
            return ''
        return f'<div class="errorlist">%s</div>' % "".join(['<p class="error">%s</p>' % e for e in self])


class LoginForm(forms.Form):
    username = forms.CharField(max_length=255, required=True)
    password = forms.CharField(max_length=255, required=True, widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    #     kwargs_new = {'error_class': PErrorList}
    #     kwargs_new.update(kwargs)
    #     super().__init__(self, *args, **kwargs_new)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data['username']
        password = cleaned_data['password']
        data = {'login': username, 'password': password}
        url = 'http://127.0.0.1:8000/server/accounts/login/'
        response = requests.post(url=url, json=data, headers={'Accept': 'application/json'})
        if response.status_code == 400:
            for error in response.json().values():
                raise forms.ValidationError(error)


class SignUpForm(forms.Form):
    username = forms.CharField(max_length=255, required=True)
    password = forms.CharField(max_length=255, required=True, widget=forms.PasswordInput())
    confirm_password = forms.CharField(max_length=255, required=True, widget=forms.PasswordInput())

    # def __init__(self, *args, **kwargs):
    #     kwargs_new = {'error_class': PErrorList}
    #     kwargs_new.update(kwargs)
    #     super().__init__(self, *args, **kwargs_new)

    def clean(self):
        cleaned_data = super().clean()
        print(cleaned_data)
        username = cleaned_data['username']
        password = cleaned_data['password']
        confirm_password = cleaned_data['confirm_password']
        if password != confirm_password:
            raise forms.ValidationError('confirm_password', 'Confirmation doesn`t match password')
        data = {'username': username, 'password': password, 'confirm_password': confirm_password}
        url = 'http://127.0.0.1:8000/server/accounts/register/'
        response = requests.post(url=url, json=data, headers={'Accept': 'application/json'})
        if response.status_code == 400:
            for field, error in response.json().items():
                raise forms.ValidationError(f'{field}: {error}')
