__author__ = 'vikram'
filename = 'data.txt'
CROSS_WIN = "Crosses win"
NOUGHTS_WIN = "Noughts win"
DRAW = "Draw"
import MySQLdb
import hashlib

conn = MySQLdb.connect(host="localhost", user="root", passwd="worldpeace", db="kmarkiv_tic")
target = open(filename, 'r')
line = target.readline()
lines = []

GAME_STATE_KEYS = ["p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8", "p9", "pos", "move", "game_id"]
GAME_STATE_TABLE = "game_states"
GAMES_KEYS = ["n_win", "c_win", "draw", "moves"]
GAMES_TABLE = "games"


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

    if (len(lines) == 8):
        k += 1
        game_id = lines[0].split(":")[0]

        print game_id
        game_cross = 0
        game_noughts = 0
        game_draw = 0

        if CROSS_WIN in lines[0]:
            game_cross = 1
        elif NOUGHTS_WIN in lines[0]:
            game_noughts = 1
        else:
            game_draw = 1
        print game_noughts, game_cross, game_draw
        games = len(lines[2].split("    ")[:-1])
        top = lines[2].split("    ")
        mid = lines[3].split("    ")
        low = lines[4].split("    ")

        for i in range(0, games):
            # print i, top[i] + mid[i] + low[i]

            # get_state(top[i] + mid[i] + low[i])
            states.append(tuple(state_data(i, game_id, top[i] + mid[i] + low[i])))

        game_data.append((game_noughts, game_cross, game_draw,i))
        if k % 1000 == 0:
            print k

            execute_many_sql(GAMES_TABLE, GAMES_KEYS, game_data)
            #execute_many_sql(GAME_STATE_TABLE, GAME_STATE_KEYS, states)
            states = []
            game_data = []

    if ":" in line:
        lines = []
        # print "start stack"
    lines.append(line)
execute_many_sql(GAMES_TABLE, GAMES_KEYS, game_data)
#execute_many_sql(GAME_STATE_TABLE, GAME_STATE_KEYS, states)

"""
SELECT AVG( moves ) , COUNT( * ) AS c, SUM( n_win ) / COUNT( * ) AS nwin, SUM( c_win ) / COUNT( * ) AS cwin, SUM( draw ) / COUNT( * ) AS dr
FROM  `game_states` g, games ga
WHERE g.`pos` LIKE  'O........'
AND g.game_id = ga.id

"""


