__author__ = 'vikram'
filename = 'Pantheon.tsv'
CROSS_WIN = "Crosses win"
NOUGHTS_WIN = "Noughts win"
DRAW = "Draw"
import MySQLdb
import hashlib

conn = MySQLdb.connect(host="localhost", user="root", passwd="worldpeace", db="pantheon")
target = open(filename, 'r')
line = target.readline()
lines = []

GAME_STATE_KEYS = ["name","en_curid","numlangs","country_code","country_code3","country","continent","birthyear","birthcity","gender","occupation","industry","domain","total_page_views","l_star","std_dev_page_views","page_views_english","page_views_non_english","average_views","hpi",]
GAME_STATE_TABLE = "pantheon"



def filter_key(key):
    if key == ".":
        return 0
    if key == "O":
        return 2
    return 1


def get_state(pos):
    keys = []
    for key in pos:
        keys.append(filter_key(key))
    # print keys
    return keys


def state_data(move, game, pos):
    pos_hash = md5_hash(pos)
    keys = get_state(pos)
    keys.extend([pos, move, game])
    # print keys
    return keys


def md5_hash(str):
    hash_object = hashlib.md5(str)
    return hash_object.hexdigest()


def execute_many_sql(table, keys, data):
    colums = ', '.join(keys)
    insert_sql = 'INSERT INTO ' + table + ' (%s) values(%s)'
    vals = ', '.join(["%s"] * len(keys))  # or whatever qparam is required
    to_execute = insert_sql % (colums, vals)
    execute_many(to_execute, data)


def execute_many(sql, queries):
    # print sql
    #print queries
    cur.executemany(
        sql,
        queries)
    id = conn.insert_id()
    conn.commit()
    print id


cur = conn.cursor()
states = []
game_data = []
k = 0
while line:
    # print line

    line = target.readline()
    line = line.replace("\n","")
    lines = line.split("\t")

    if (len(lines) == len(GAME_STATE_KEYS)):
        game_data.append(lines)
        k+=1
        if k % 1000 == 0:
            execute_many_sql(GAME_STATE_TABLE, GAME_STATE_KEYS, game_data)
            game_data = []


execute_many_sql(GAME_STATE_TABLE, GAME_STATE_KEYS, game_data)
game_data = []