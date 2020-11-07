from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import ChessUser


class ImageForm(forms.Form):
    photo = forms.ImageField()


class ChessUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = ChessUser
        fields = ('username', )
