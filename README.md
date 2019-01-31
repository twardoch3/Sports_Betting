# Sports_Betting
The Sport_Betting Project is a program for making forecasts about basketball games and managing database with users' game forecasts, bets and prediction statistics.

### Requirements
Program requires PostgreSQL database and Django.

### Installing
Create database 'sbet_db'. Install requirements  with command:
```
pip install -r requirements.txt
```
### Running the program
Apply the migrations:
```
python manage.py migrate
```
Start a development Web server on the local machine with command:
```
python manage.py runserver
```

### Usage Examples:
For example data run ```python3 scores.py``` to get today's games and results from 'http://www.espn.com/nba/scoreboard/'.
Type in ```g``` to download games and ```r``` for results (if available).
(Connection info: username = 'postgres', password = 'coderslab')

Add Forecasts:
```
http://127.0.0.1:8000/betting/
```
Add Bet:
```
http://127.0.0.1:8000/betting/bet/new/
```
Statistics:
```
http://127.0.0.1:8000/betting/statistics/
```





