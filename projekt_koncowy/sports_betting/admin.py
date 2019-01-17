from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

admin.site.register(User, UserAdmin)
admin.site.register(Team)
admin.site.register(GameForecast)
admin.site.register(Bookmaker)
admin.site.register(Opinion)
admin.site.register(YourBetResult)
admin.site.register(YourBet)


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['id', 'game_date', 'team_home', 'team_away']


@admin.register(GameResult)
class GameAdmin(admin.ModelAdmin):
    list_display = ['id', 'game', 'winner']
