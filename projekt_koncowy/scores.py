from requests_html import HTMLSession
from psycopg2 import connect
from psycopg2.extras import RealDictCursor
import datetime


class DB:
    username = "postgres"
    passwd = "coderslab"
    hostname = "localhost"
    db_name = "sbet_db"

    def connect(self):
        self.cnx = connect(user=self.username, password=self.passwd, host=self.hostname, database=self.db_name)
        return self.cnx

    def select(self, sql):
        cnx = self.connect()
        with cnx.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(sql)
            self.data = [row for row in cursor]
            cnx.commit()
        cnx.close()

    def insert(self, sql, values):
        cnx = self.connect()
        with cnx.cursor() as cursor:
            cursor.execute(sql, values)
            if 'returning' in sql:
                self.ids = cursor.fetchone()
            cnx.commit()
        cnx.close()


# schedule_results = 'span.sb-team-short' or 'td.total'

def download(schedule_results):
    # dodawanie meczy
    teams_list = []
    l = []
    session = HTMLSession()
    r = session.get('http://www.espn.com/nba/scoreboard/_/date/20190115')  # bez daty bedzie sciagac dzisiejsze mecze  #/_/date/20190101
    r.html.render()
    for tag in r.html.find(
            schedule_results):  # for tag in r.html.find('td.total') or for tag in r.html.find('span.sb-team-short')
        l.append(tag.text)
    return l


if __name__ == '__main__':

    option = input('Download games/results? (g/r)')

    if option == 'g':
        # schedule
        l = download('span.sb-team-short')

        i = 0
        while i < len(l):
            sql1 = "Select id from  sports_betting_team WHERE NAME = '%s' ;" % l[i]
            sql2 = "Select id from  sports_betting_team WHERE NAME = '%s' ;" % l[i + 1]
            sql3 = "Insert into sports_betting_game (team_away_id,team_home_id, game_date ) VALUES (%s,%s,%s) returning id;"
            db_action1 = DB()
            db_action2 = DB()
            db_action1.select(sql1)
            db_action2.select(sql2)
            print(l[i])
            print(l[i + 1])
            print(db_action1.data[0])
            print(db_action2.data[0])
            db_action1.insert(sql3, (
                db_action1.data[0]['id'], db_action2.data[0]['id'], datetime.datetime.today()))  # uwaga na daty
            # game_ids.append(db_action1.ids[0])
            i += 2
        print('Schedule updated')

    elif option == 'r':
        # results
        r = download('td.total')

        # r to results
        sql4 = "select sports_betting_game.id from sports_betting_game left join sports_betting_gameresult on sports_betting_game.id=sports_betting_gameresult.game_id where sports_betting_gameresult.id is null order by id;"
        db_action3 = DB()
        db_action3.select(sql4)
        game_ids = [e['id'] for e in db_action3.data]
        print(game_ids)
        print(r)

        # results
        i = 0
        j = 0
        while i < len(r):
            sql5 = "Insert into sports_betting_gameresult (winner, team_away_score,team_home_score, game_id ) VALUES (%s,%s,%s,%s);"
            db_action4 = DB()
            if int(r[i]) > int(r[i + 1]):
                winner = 2
            else:
                winner = 1
            db_action4.insert(sql5, (winner, r[i], r[i + 1], game_ids[j]))
            j += 1
            i += 2
        print('Results updated')

    else:
        print('wrong input')


