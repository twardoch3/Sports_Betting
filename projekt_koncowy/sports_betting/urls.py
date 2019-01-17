from django.urls import path
from .views import (
    TodayGamesView,
    ForecastsListView,
    AddRealBetView,
    BetsListView,
    BetDetailsView,
    EditBetView,
    StatisticsView,
    UpdateForecastView,
    BookmakersView,
    BookmakerOpinionsView,
    GameView,
    AddBookmakerView,
    BetPictureView,
    GamesView,
    UserRankingView,
)

urlpatterns = [
    path('', TodayGamesView.as_view(), name='today_games'),
    path('forecasts/<int:pk>', ForecastsListView.as_view(), name='forecasts'),
    path('forecast/edit/<int:pk>', UpdateForecastView.as_view(), name='edit_forecast'),
    # edit forecast
    # bets
    path('my_bets/', BetsListView.as_view(), name='bets_list'),
    path('my_bets/<str:sort>/', BetsListView.as_view(), name='bets_list_sort'),
    path('bet/new', AddRealBetView.as_view(), name='add_bet'),
    path('bet/<int:pk>', BetDetailsView.as_view(), name='bet_details'),
    path('bet/picture/<int:pk>', BetPictureView.as_view(), name='bet_picture'),
    path('bet/edit/<int:pk>', EditBetView.as_view(), name='edit_bet'),

    # statistics
    path('statistics/', StatisticsView.as_view(), name='statistics'),

    # bookmakers
    path('bookmakers/', BookmakersView.as_view(), name='bookmakers'),
    path('bookmaker/<int:pk>', BookmakerOpinionsView.as_view(), name='bookmaker_opinions'),
    path('bookmaker/new', AddBookmakerView.as_view(), name='add_bookmaker'),
    # games
    path('game/<int:pk>', GameView.as_view(), name='game_details'),
    path('games', GamesView.as_view(), name='games'),
    path('ranking', UserRankingView.as_view(), name='ranking'),

]
