__author__ = 'vikram'
filename = 'Pantheon.tsv'
CROSS_WIN = "Crosses win"
NOUGHTS_WIN = "Noughts win"
DRAW = "Draw"

import MySQLdb
import MySQLdb.cursors

conn = MySQLdb.connect(host="localhost", user="root", passwd="worldpeace", db="pantheon",
                       cursorclass=MySQLdb.cursors.DictCursor)
target = open(filename, 'r')
line = target.readline()
lines = []

GAME_STATE_KEYS = ["name", "en_curid", "numlangs", "country_code", "country_code3", "country", "continent", "birthyear",
                   "birthcity", "gender", "occupation", "industry", "domain", "total_page_views", "l_star",
                   "std_dev_page_views", "page_views_english", "page_views_non_english", "average_views", "hpi", ]
GAME_STATE_TABLE = "pantheon"

db = conn
db.set_character_set('utf8')
cur = conn.cursor()
dbc = cur
dbc.execute('SET NAMES utf8;')
dbc.execute('SET CHARACTER SET utf8;')
dbc.execute('SET character_set_connection=utf8;')
TABLE = "hpi_occupation"
keys = ["occupation", "hpi_avg", "hpi_sum", "hpi_percent", "year", "country"]


def get_mysql_data(sql):
    cur = conn.cursor()
    cur.execute(sql)
    data = cur.fetchall()
    return data


def update_sql(data, id):
    print data, id
    SQL = "UPDATE hpi_occupation SET hpi_cum=%s WHERE id=%s "
    cur.execute(
        SQL,
        (data, id))


k = 0
sql = "SELECT * FROM pantheon GROUP BY occupation"
data = get_mysql_data(sql)
for row in data:
    sql = "SELECT * FROM hpi_occupation WHERE occupation='%s' ORDER BY year ASC" % row['occupation']
    countries = get_mysql_data(sql)
    hpi_sum_data = {}
    for age in countries:
        hpi_sum = hpi_sum_data.get(age['country'], 0)
        hpi_sum += age['hpi_sum']
        hpi_sum_data[age['country']] = hpi_sum
        k += 1
        update_sql(hpi_sum, age['id'])
        if k % 100 == 0:
            id = conn.insert_id()
            print id
            conn.commit()


