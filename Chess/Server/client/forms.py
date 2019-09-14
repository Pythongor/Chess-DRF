from django import forms
from django.core.validators import RegexValidator

validator = RegexValidator(regex='^[A-Ha-h][1-8]$')


class PlayerMoveForm(forms.Form):
    start = forms.CharField(max_length=2, validators=[validator, ],
                            label='Start', help_text='"e2"')
    end = forms.CharField(max_length=2, validators=[validator, ],
                          label='End', help_text='"e4"')