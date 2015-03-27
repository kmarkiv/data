import re

__author__ = 'vikram'

from optparse import OptionParser
from iniparse import INIConfig
from cStringIO import StringIO
from flask import Flask, g, render_template, request, jsonify
import MySQLdb
import MySQLdb.cursors

parser = OptionParser(usage="Usage: %prog [options] filename")
parser.add_option("-e", "--environment", dest="environment", help="Set the application environment")
(options, args) = parser.parse_args()

if options.environment:
    env = options.environment
else:
    env = 'production'

config_text = """
[production]
database = kmarkiv_tic
username = kmarkiv_green
password = GreenScore
debug = enabled
host =127.0.0.1

[kmarkiv]
database = kmarkiv_tic
username = root
password = worldpeace
debug = enabled
host =127.0.0.1
"""

WIN_PATTERN = '|'.join([
    'XXX......',
    '...XXX...',
    '......XXX',
    'X..X..X..',
    '.X..X..X.',
    '..X..X..X',
    'X...X...X',
    '..X.X.X..',
])
WIN_RE = {
    'X': re.compile(WIN_PATTERN),
    'O': re.compile(WIN_PATTERN.replace('X', 'O')),
}


def get_data(env="aws"):
    f = StringIO(config_text)
    cfg = INIConfig(f)
    config = cfg[env]
    return config


def get_db():
    """
    :rtype : object
    """
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = MySQLdb.connect(host=app.config['DATA']['host'],
                                           user=app.config['DATA']['username'],
                                           passwd=app.config['DATA']['password'],
                                           db=app.config['DATA']['database'],
                                           cursorclass=MySQLdb.cursors.DictCursor
        )
    return db


app = Flask(__name__)
app.config['DATA'] = get_data(env)
app.debug = True


def get_data(conn, sql):
    cur = conn.cursor()
    cur.execute(sql)
    data = cur.fetchall()
    return data


def get_position_percent(pos):
    conn = get_db()
    sql = "SELECT AVG( moves ) as avg , COUNT( * ) AS c, 100*SUM( n_win ) / COUNT( * ) AS nwin, 100*SUM( c_win ) / COUNT( * ) AS cwin, 100*SUM( draw ) / COUNT( * ) AS dr FROM  `game_states` g, games ga WHERE g.`pos` LIKE  '%s' AND g.game_id = ga.id" % (
        pos)
    return get_data(conn, sql)


def get_all_position():
    conn = get_db()
    sql = "SELECT AVG( moves ) as avg , COUNT( * ) AS c, 100*SUM( n_win ) / COUNT( * ) AS nwin, 100*SUM( c_win ) / COUNT( * ) AS cwin, 100*SUM( draw ) / COUNT( * ) AS dr FROM  `games` g"
    return get_data(conn, sql)


def get_next_position(pos):
    conn = get_db()
    pos = pos if "." in pos else "........."
    move = "X" if pos.count("X") < pos.count("O") else "O"
    oponent_move = "O" if move == "X" else "O"
    combs = []
    heat = {}
    for i, c in enumerate(pos):
        if c == ".":
            string = pos[0:i] + move + pos[i + 1:]
            ostring = pos[0:i] + oponent_move + pos[i + 1:]
            combs.append(string)
            heat[string] = {"pos": i + 1, "win": 1 if WIN_RE[move].match(string) else 0,
                            "loss": 1 if WIN_RE[oponent_move].match(ostring) else 0}
    comb_list = "','".join(combs)
    sql = "SELECT pos, AVG( moves ) AS avg, COUNT( * ) AS c, 100 * SUM( n_win ) / COUNT( * ) AS nwin, 100 * SUM( c_win ) / COUNT( * ) AS cwin, 100 * SUM( draw ) / COUNT( * ) AS dr FROM  `game_states` g, games ga WHERE g.`pos` IN ('%s') AND g.game_id = ga.id GROUP BY pos" % comb_list
    # print sql
    pos_index = "cwin" if move == "X" else "nwin"
    moves = get_data(conn, sql)
    best_move = 0
    play = 1
    for lay in moves:
        # print lay
        if lay['pos'] in heat:
            heat[lay['pos']]['data'] = lay
            heat[lay['pos']]['score'] = max(200 * heat[lay['pos']]['win'], 100 * heat[lay['pos']]['loss'],
                                            lay[pos_index])
            if best_move < heat[lay['pos']]['score']:
                play = heat[lay['pos']]['pos']
                best_move = heat[lay['pos']]['score']
    return heat, best_move, play


@app.context_processor
def path():
    if env == "production":
        path = ""
    else:
        path = ""
    return dict(relative_path=path, ga=app.config['DATA']['google_analytics'])


@app.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    # if (exception is not None):
    # capture_request_data(exception, 500)


    # if exception is not None:
    # error_handle(exception)
    if db is not None:
        db.close()


@app.route('/')
def hello_world():
    return render_template('admin.html')


@app.route('/api/pos')
def get_pos():
    pos = request.args.get('pos', '')
    heat, best_move, play = get_next_position(pos)
    if "." in pos:
        RAW = get_position_percent(pos)
    else:
        RAW = get_all_position()
    print RAW
    # return 'Hello World!'
    return jsonify({"data": RAW[0], "heat": heat, "best": best_move, "play": play})


if __name__ == '__main__':
    app.run()