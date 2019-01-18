# Sports_Betting
Application allows to make a forecasts about basketball games and manage database with users' game forecasts, bets
and prediction statistics ("miniportal" for sports betting).

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
For example data run ```scores.py``` to get today's games and results. 
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





