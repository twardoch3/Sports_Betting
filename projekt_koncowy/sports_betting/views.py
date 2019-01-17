from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.views import View
from django.views import generic
from .models import (
    Game,
    GameForecast,
    YourBet,
    YourBetResult,
    Bookmaker,
    User,
)
from .forms import (
    YourForecastForm,
    BetForm,
    OpinionForm,
    CommentForm,
    CreateUserForm,
    EditUser,
    InfoForm,
)
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
import datetime
from django.http import Http404


class CreateEditUserView(View):
    def get(self, request):
        if request.user.is_authenticated:
            form = EditUser(instance=request.user)
            t = 'Edit User'
        else:
            t = 'Create New User'
            form = CreateUserForm()
        ctx = {'form': form, 't': t}
        return render(request, 'sports_betting/create_edit_user.html', ctx)

    def post(self, request):
        if request.user.is_authenticated:
            form = EditUser(request.POST, instance=request.user)
            t = 'Edit User'
        else:
            t = 'Create New User'
            form = CreateUserForm(request.POST)
        ctx = {'form': form}
        if form.is_valid():
            form.save()
            if 'New' in t:
                # logowanie
                raw_password = form.cleaned_data.get('password1')
                user = authenticate(username=form.instance.username, password=raw_password)
                login(request, user)
            return redirect('/')

        return render(request, 'sports_betting/create_edit_user.html', ctx)


class DeleteUserAccountView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = User
    success_url = '/'

    def test_func(self):
        return self.request.user == self.get_object()


class TodayGamesView(LoginRequiredMixin, generic.ListView):
    template_name = 'sports_betting/base.html'
    queryset = Game.objects.filter(game_date=datetime.date.today()).order_by('id')  # tylko dzisiejsze mecze

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = YourForecastForm()
        context['f'] = GameForecast.objects.filter(user=self.request.user, date=datetime.datetime.today())
        return context

    def post(self, request, *args, **kwargs):
        # form = YourForecastForm(request.POST)
        fs = request.POST.getlist('your_forecast')
        i = 0
        for g in self.queryset:
            GameForecast.objects.create(user=self.request.user, game=g, your_forecast=fs[i])
            i += 1
        return redirect('forecasts', pk=self.request.user.pk)


class ForecastsListView(LoginRequiredMixin, generic.ListView):
    template_name = 'sports_betting/forecasts.html'

    # paginate_by = 20
    def get_queryset(self):
        self.user = get_object_or_404(User, pk=self.kwargs.get('pk'))
        return GameForecast.objects.filter(user=self.user).order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.pk == self.kwargs.get('pk'):
            x = 'My Forecasts'
        else:
            x = 'User {} Forecasts'.format(User.objects.filter(pk=self.kwargs.get('pk'))[0])
        context['x'] = x
        return context


class UpdateForecastView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = GameForecast
    form_class = YourForecastForm
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return '/betting/forecasts/{}'.format(self.request.user.pk)

    def test_func(self):
        return self.request.user == self.get_object().user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['f'] = self.get_object()
        return context


class AddRealBetView(LoginRequiredMixin, generic.CreateView):
    form_class = BetForm
    model = YourBet

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        g = GameForecast.objects.filter(user=self.request.user, date=datetime.datetime.today())
        context['form'].fields['games'].queryset = g  # tylko dzisiejsze mecze
        context['g'] = g
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        self.object = form.save()
        YourBetResult.objects.create(bet=self.object)
        return super().form_valid(form)


class EditBetView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    form_class = BetForm
    model = YourBet

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        g = self.get_object().games.all()
        context['form'].fields['games'].queryset = g
        context['g'] = g
        return context

    def test_func(self):
        return self.request.user == self.get_object().user


class BetPictureView(LoginRequiredMixin, View):
    def get(self, request, pk):
        bet = get_object_or_404(YourBet, pk=pk)
        if bet.user == request.user or bet.visible:
            ctx = {'bet': bet}
            return render(request, 'sports_betting/bet_image.html', ctx)
        else:
            raise Http404


class BetsListView(LoginRequiredMixin, generic.ListView):
    model = YourBet
    template_name = 'sports_betting/bets_list.html'
    ordering = '-date'

    def get_queryset(self):
        s = self.kwargs.get('sort')
        if s == 'loss':
            return YourBet.objects.filter(user=self.request.user).order_by('yourbetresult__bet_result')
        elif s == 'profit':
            self.ordering = '-yourbetresult__bet_result'
            return YourBet.objects.filter(user=self.request.user).order_by('-yourbetresult__bet_result')
        else:
            return YourBet.objects.filter(user=self.request.user)

    def get(self, request, sort=None, *args,
            **kwargs, ):
        for bet in YourBet.objects.filter(user=self.request.user):  # filter z data
            if bet.bet_won_lost():
                if bet.bet_won_lost() == 'Bet Won':
                    YourBetResult.objects.filter(bet=bet).update(bet_result=bet.assumable_prize)
                else:
                    YourBetResult.objects.filter(bet=bet).update(bet_result=bet.your_bid * (-1))

        return super().get(request, *args, **kwargs)


class BetDetailsView(LoginRequiredMixin, generic.DetailView):
    model = YourBet

    def get_object(self, queryset=None):
        obj = super().get_object()
        if obj.user == self.request.user:
            return obj
        else:
            if obj.visible:
                return obj
            else:
                raise Http404

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = InfoForm()
        return context

    def post(self, request, pk, *args, **kwargs):
        ytr = get_object_or_404(YourBetResult, pk=pk)
        form = InfoForm(request.POST, instance=ytr)
        if form.is_valid():
            form.save()
            return redirect(self.get_object())


class BookmakersView(LoginRequiredMixin, generic.ListView):
    model = Bookmaker


class AddBookmakerView(LoginRequiredMixin, generic.CreateView):
    model = Bookmaker
    fields = ['name', 'location']


class BookmakerOpinionsView(LoginRequiredMixin, generic.DetailView):
    model = Bookmaker

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = OpinionForm()
        return context

    def post(self, request, *args, **kwargs):
        form = OpinionForm(request.POST)
        if form.is_valid():
            form.instance.user = request.user
            form.instance.bookmaker = self.get_object()
            form.save()
            return redirect(self.get_object())


class StatisticsView(LoginRequiredMixin, View):
    def get(self, request):
        # f
        forecasts = self.request.user.user_correct_forecasts_percentage()
        fn = self.request.user.gameforecast_set.all().count()

        # b
        bets = self.request.user.user_correct_bets_percentage()
        bn = self.request.user.yourbet_set.all().count()

        money_b = sum([int(r.yourbetresult.bet_result) for r in YourBet.objects.filter(user=self.request.user)])
        try:
            bloss = min([int(r.yourbetresult.bet_result) for r in YourBet.objects.filter(user=self.request.user) if
                         int(r.yourbetresult.bet_result) < 0])
        except ValueError:
            bloss = 0
        try:
            bprofit = max([int(r.yourbetresult.bet_result) for r in YourBet.objects.filter(user=self.request.user) if
                           int(r.yourbetresult.bet_result) > 0])
        except ValueError:
            bprofit = 0

        ctx = {'fn': fn, 'bn': bn, 'fcorrect': forecasts['fcorrect'], 'ffailed': forecasts['ffailed'],
               'bcorrect': bets['bcorrect'], 'bfailed': bets['bfailed'],
               'f_win_percentage': forecasts['percentage'], 'b_win_percentage': bets['percentage'], 'money_b': money_b,
               'bprofit': bprofit, 'bloss': bloss}

        return render(request, 'sports_betting/statistics.html', ctx)


class GameView(LoginRequiredMixin, generic.DetailView):
    model = Game

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        return context

    def post(self, request, *args, **kwargs):
        form = CommentForm(request.POST)
        if form.is_valid():
            form.instance.user = request.user
            form.instance.game = self.get_object()
            form.save()
            return redirect(self.get_object())


class GamesView(LoginRequiredMixin, generic.ListView):
    model = Game
    ordering = '-game_date'
    paginate_by = 25


class UserRankingView(LoginRequiredMixin, generic.ListView):
    model = User
