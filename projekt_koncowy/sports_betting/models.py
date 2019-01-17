from django.db import models
from django.urls import reverse_lazy
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class User(AbstractUser):
    favorite_team = models.CharField(max_length=50, blank=True)
    favorite_player = models.CharField(max_length=50, blank=True)
    loss_alert = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('email',)

    def __str__(self):
        return self.username

    def user_correct_forecasts_percentage(self):
        fcorrect = 0
        ffailed = 0
        for f in self.gameforecast_set.all():
            if f.forecast_result() == 'Correct':
                fcorrect += 1
            elif f.forecast_result() == 'Failed':
                ffailed += 1
        if (fcorrect + ffailed):
            p = str(round(fcorrect / (fcorrect + ffailed) * 100, 2)) + '%'
        else:
            p = '0%'
        return {'fcorrect': fcorrect, 'ffailed': ffailed,
                'percentage': p}

    def user_correct_bets_percentage(self):
        bcorrect = 0
        bfailed = 0
        for b in self.yourbet_set.all():
            if b.bet_won_lost() == 'Bet Won':
                bcorrect += 1
            elif b.bet_won_lost() == 'Bet Failed':
                bfailed += 1
        if (bcorrect + bfailed):
            p = str(round(bcorrect / (bcorrect + bfailed) * 100, 2)) + '%'
        else:
            p = '0%'
        return {'bcorrect': bcorrect, 'bfailed': bfailed,
                'percentage': p}


class Team(models.Model):
    name = models.CharField(max_length=70, unique=True)
    city = models.CharField(max_length=70)
    conference = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.city} {self.name}'


class Bookmaker(models.Model):
    name = models.CharField(max_length=70, unique=True)
    location = models.CharField(max_length=70, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse_lazy('bookmaker_opinions', kwargs={'pk': self.id})


class Game(models.Model):
    team_home = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_home')
    team_away = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_away')
    game_date = models.DateField()

    class Meta:
        unique_together = ('team_home', 'team_away', 'game_date')

    def __str__(self):
        return f'{self.team_away} at {self.team_home}'

    def get_absolute_url(self):
        return reverse_lazy('game_details', kwargs={'pk': self.id})

    def forecast_users_home_team_percentage(self):
        fhome = 0
        faway = 0
        for f in self.gameforecast_set.all():
            if f.your_forecast == 1:
                fhome += 1
            else:
                faway += 1
        if not (fhome + faway):
            return '0%'
        else:
            return str(fhome / (fhome + faway) * 100) + '%'

    def users_correct_forecasts_percentage(self):
        fcorrect = 0
        ffailed = 0
        for f in self.gameforecast_set.all():
            if f.forecast_result() == 'Correct':
                fcorrect += 1
            elif f.forecast_result() == 'Failed':
                ffailed += 1
        if not (fcorrect + ffailed):
            return '0%'
        else:
            return str(fcorrect / (fcorrect + ffailed) * 100) + '%'


class GameResult(models.Model):
    choices_winner = ((1, 'home_team'),
                      (2, 'away_team'))

    game = models.OneToOneField(Game, on_delete=models.CASCADE)
    winner = models.PositiveSmallIntegerField(choices=choices_winner)
    team_home_score = models.PositiveSmallIntegerField()
    team_away_score = models.PositiveSmallIntegerField()

    # overtime = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.team_home_score} - {self.team_away_score}'

    def win_team(self):
        if self.winner == 1:
            return self.game.team_home
        else:
            return self.game.team_away


class GameForecast(models.Model):
    your_pick = (
        (1, '1 - home team'),
        (2, '2 - away team')
    )
    date = models.DateField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)  # tu musi byc foreign key!!!!
    your_forecast = models.SmallIntegerField(choices=your_pick)

    def __str__(self):
        return f"{self.game} - Your Pick - {self.get_your_forecast_display()}"

    def forecast_result(self):
        r = GameResult.objects.filter(game=self.game)
        if not r:
            return False
        elif r[0].winner == self.your_forecast:
            return 'Correct'
        else:
            return 'Failed'


class YourBet(models.Model):
    date = models.DateField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.SET_NULL, null=True, blank=True)
    assumable_prize = models.PositiveIntegerField()
    your_bid = models.PositiveIntegerField()
    games = models.ManyToManyField(GameForecast)
    image = models.ImageField(null=True, blank=True, width_field='width_field', height_field='height_field')
    height_field = models.IntegerField(default=300, null=True, blank=True)
    width_field = models.IntegerField(default=100, null=True, blank=True)
    visible = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.bookmaker} - {self.date} - bid: {self.your_bid}'

    def get_absolute_url(self):
        return reverse_lazy('bet_details', kwargs={'pk': self.id})

    def bet_won_lost(self):
        for g in self.games.all():
            if not g.forecast_result():
                return False
            elif g.forecast_result() == 'Failed':
                return 'Bet Failed'
        return 'Bet Won'


class YourBetResult(models.Model):
    bet = models.OneToOneField(YourBet, on_delete=models.CASCADE)
    info = models.TextField(blank=True, null=True)
    bet_result = models.SmallIntegerField(default=0)


class Opinion(models.Model):
    text = models.TextField()
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    creation_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text[:20] + '...'


class Comment(models.Model):
    text = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    creation_date = models.DateTimeField(auto_now=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    def __str__(self):
        return self.text[:20] + '...'
