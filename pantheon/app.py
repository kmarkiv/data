from optparse import OptionParser
from cStringIO import StringIO

from iniparse import INIConfig
from flask import Flask, g, render_template
import MySQLdb
import MySQLdb.cursors


API_KEY = "AIzaSyCfRmwMKY8NVG1YSP_bJzA44orhsZOtjmY"
TABLE_ID = "1R0Pu0hjxXGWQC_eUetkV_1pZvN0hVubQaBY_RDtp"
from apiclient.discovery import build
# https://www.google.com/fusiontables/data?docid=1HLka9ST2CZW9EE8kQkrw8FACWEttqFEqrzYPkf3N#rows:id=1
service = build('fusiontables', 'v1', developerKey=API_KEY)

DEBUG = True

KEY = "13PuNPw7E4-vPkYDyOSdZDiT8WYzv-WwEevqH3CrB"

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
password =
debug = enabled
host =127.0.0.1
[kmarkiv]
database = pantheon
username = root
password = worldpeace
debug = enabled
host =127.0.0.1
"""


def get_data(env="aws"):
    f = StringIO(config_text)
    cfg = INIConfig(f)
    config = cfg[env]
    return config


app = Flask(__name__)
app.config['DATA'] = get_data(env)
app.debug = True


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


def get_mysql_data(conn, sql):
    cur = conn.cursor()
    cur.execute(sql)
    data = cur.fetchall()
    return data


@app.route('/')
def hello_world():
    service = build('fusiontables', 'v1', developerKey=API_KEY)
    query = "SELECT wiki_key,title,start,end,country,continent FROM " + TABLE_ID + " "
    response = service.query().sql(sql=query).execute()
    # print response
    return render_template('home.html', list=response['rows'])


@app.route('/searchs', methods=["GET"])
def hello_search():
    query = "SELECT COUNT(*) as counts,country FROM pantheon GROUP BY country ORDER BY counts DESC LIMIT 40"
    conn = get_db()
    country = get_mysql_data(conn, query)

    query = "SELECT COUNT(*) as counts,gender FROM pantheon GROUP BY gender ORDER BY counts DESC LIMIT 40"
    conn = get_db()
    gender = get_mysql_data(conn, query)

    query = "SELECT COUNT(*) as counts,domain FROM pantheon GROUP BY domain ORDER BY counts DESC LIMIT 40"
    conn = get_db()
    domain = get_mysql_data(conn, query)

    return render_template('home.html', domain=domain, gender=gender, country=country)


@app.route('/search', methods=["GET"])
def hello_search_stuff():
    START = 1400
    END = 1700
    CONTINENT = "Europe"
    query = "SELECT COUNT(*) as counts,country FROM pantheon WHERE birthyear>'%s' AND birthyear<'%s' AND continent='%s' GROUP BY country ORDER BY counts DESC LIMIT 40" % (
    START, END, CONTINENT)

    conn = get_db()
    country = get_mysql_data(conn, query)

    query = "SELECT COUNT(*) as counts,gender FROM pantheon WHERE birthyear>'%s' AND birthyear<%s AND continent='%s' GROUP BY gender ORDER BY counts DESC LIMIT 40" % (
    START, END, CONTINENT)
    conn = get_db()
    gender = get_mysql_data(conn, query)

    query = "SELECT COUNT(*) as counts,domain FROM pantheon WHERE birthyear>%s AND birthyear<%s AND continent='%s' GROUP BY domain ORDER BY counts DESC LIMIT 40" % (
    START, END, CONTINENT)
    conn = get_db()
    domain = get_mysql_data(conn, query)

    query = "SELECT COUNT(*) as counts,occupation FROM pantheon WHERE birthyear>'%s' AND birthyear<%s AND continent='%s' GROUP BY occupation ORDER BY counts DESC LIMIT 40" % (
    START, END, CONTINENT)
    conn = get_db()
    occupation = get_mysql_data(conn, query)

    return render_template('home.html', domain=domain, gender=gender, country=country, occupation=occupation)


if __name__ == '__main__':
    app.run(debug=DEBUG)
"""" \
146	Persian_Empire	Persian Empires	-550	651

"""