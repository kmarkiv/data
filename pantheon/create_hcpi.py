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


def execute_many_sql(table, keys, data):
    colums = ', '.join(keys)
    insert_sql = 'INSERT INTO ' + table + ' (%s) values(%s)'
    vals = ', '.join(["%s"] * len(keys))  # or whatever qparam is required
    to_execute = insert_sql % (colums, vals)
    execute_many(to_execute, data)


def execute_many(sql, queries):
    # print sql
    # print queries
    cur.executemany(
        sql,
        queries)
    id = conn.insert_id()
    conn.commit()
    print id


sql = "SELECT * FROM pantheon GROUP BY occupation"
data = get_mysql_data(sql)
game_data = []
k = 0


def add_hcpi_data(data):
    global game_data
    for row in data:
        add_sum_data(row)


def update_data():
    global game_data
    execute_many_sql(TABLE, keys, game_data)
    game_data = []

def add_sum_data(row):
    global k
    k += 1
    global game_data
    game_data.append(
        (row["occupation"], row["hpi_avg"], row["hpi_sum"], row["hpi_percent"], row["year"], row["country"]))
    if k % 100 == 0:
        update_data()



for row in data:
    for i in range(-1000, 2000, 100):
        print i, i + 100
        print row['occupation']
        sql = "SELECT occupation,%s as year,sum(hpi) as hpi_sum,avg(hpi) as hpi_avg,100 as hpi_percent,'all'as country FROM pantheon WHERE birthyear>%s AND birthyear<=%s AND occupation='%s'" % (
            i + 100, i, i + 100, row['occupation'])

        c_data = get_mysql_data(sql)
        if c_data[0]['hpi_sum'] is not None:
            add_hcpi_data(c_data)
            sql = "SELECT occupation,%s as year,sum(hpi) as hpi_sum,avg(hpi) as hpi_avg,sum(hpi)/%s as hpi_percent,country FROM pantheon WHERE birthyear>%s AND birthyear<=%s AND occupation='%s' GROUP BY country" % (
                i + 100, c_data[0]['hpi_sum'], i, i + 100, row['occupation'])
            o_data = get_mysql_data(sql)
            add_hcpi_data(o_data)
            print o_data

print len(data)
update_data()


# get all occupations
# group by country for occupation -1000 2000,100


