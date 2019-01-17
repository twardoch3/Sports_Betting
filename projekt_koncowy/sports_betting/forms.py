import django.forms as forms
from .models import GameForecast, YourBet, Opinion, Comment, User, Game, YourBetResult
from django.contrib.auth.forms import UserCreationForm


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class EditUser(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'favorite_team', 'favorite_player', 'loss_alert']


class YourForecastForm(forms.ModelForm):
    class Meta:
        model = GameForecast
        fields = ['your_forecast']


class BetForm(forms.ModelForm):  # data tylko dzisiejsza!
    class Meta:
        model = YourBet
        exclude = ['user', 'height_field', 'width_field', 'date']
        widgets = {
            'games': forms.CheckboxSelectMultiple(),

        }

        # def __init__(self, *args, **kwargs):
        #     super(BetForm, self).__init__(*args, **kwargs)
        #     for field in self.fields:
        #         self.fields[field].widget.attrs.update({
        #             'class': 'form-control'
        #         })


class OpinionForm(forms.ModelForm):
    class Meta:
        model = Opinion
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'cols': 50}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'cols': 50}),
        }


class InfoForm(forms.ModelForm):
    class Meta:
        model = YourBetResult
        fields = ['info']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'cols': 50}),
        }
