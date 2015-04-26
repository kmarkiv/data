from optparse import OptionParser
from cStringIO import StringIO

from iniparse import INIConfig
from flask import Flask, g, render_template, request
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
                                           cursorclass=MySQLdb.cursors.DictCursor, charset='utf8'
        )
    return db


def get_mysql_data(sql):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(sql)
    data = cur.fetchall()
    return data


@app.route('/')
def hello_world():
    query = "SELECT id,wiki_key,title,start,end,country,continent FROM wiki_era"
    data = get_mysql_data(query)  # print response

    query = "SELECT id,occupation FROM pantheon GROUP BY occupation"
    occupations = get_mysql_data(query)

    return render_template('home.html', list=data, occupations=occupations)


@app.route('/searchs', methods=["GET"])
def hello_search():
    query = "SELECT COUNT(*) as counts,country FROM pantheon GROUP BY country ORDER BY counts DESC LIMIT 40"
    country = get_mysql_data(query)

    query = "SELECT COUNT(*) as counts,gender FROM pantheon GROUP BY gender ORDER BY counts DESC LIMIT 40"
    gender = get_mysql_data(query)

    query = "SELECT COUNT(*) as counts,domain FROM pantheon GROUP BY domain ORDER BY counts DESC LIMIT 40"
    domain = get_mysql_data(query)

    return render_template('home.html', domain=domain, gender=gender, country=country)


def search_era_stuff(START, END, CONTINENT, COUNTRY='%'):
    query = "SELECT COUNT(*) as counts,country FROM pantheon WHERE birthyear>'%s' AND birthyear<'%s' AND continent='%s' AND country='%s' GROUP BY country ORDER BY counts DESC LIMIT 40" % (
        START, END, CONTINENT, COUNTRY)

    country = get_mysql_data(query)

    query = "SELECT COUNT(*) as counts,gender FROM pantheon WHERE birthyear>'%s' AND birthyear<%s AND continent='%s' AND country='%s' GROUP BY gender ORDER BY counts DESC LIMIT 40" % (
        START, END, CONTINENT, COUNTRY)

    gender = get_mysql_data(query)

    query = "SELECT COUNT(*) as counts,domain FROM pantheon WHERE birthyear>%s AND birthyear<%s AND continent='%s' AND country='%s' GROUP BY domain ORDER BY counts DESC LIMIT 40" % (
        START, END, CONTINENT, COUNTRY)

    domain = get_mysql_data(query)

    query = "SELECT COUNT(*) as counts,occupation FROM pantheon WHERE birthyear>'%s' AND birthyear<%s AND continent='%s' AND country='%s' GROUP BY occupation ORDER BY counts DESC LIMIT 40" % (
        START, END, CONTINENT, COUNTRY)
    occupation = get_mysql_data(query)
    return country, gender, domain, occupation


def search_occupation_stuff(OCCUPATION):
    query = "SELECT COUNT(*) as counts,country FROM pantheon WHERE occupation='%s' GROUP BY country ORDER BY counts DESC LIMIT 40" % (
        OCCUPATION)

    country = get_mysql_data(query)

    query = "SELECT COUNT(*) as counts,gender FROM pantheon WHERE occupation='%s' GROUP BY gender ORDER BY counts DESC LIMIT 40" % (
        OCCUPATION)

    gender = get_mysql_data(query)

    query = "SELECT COUNT(*) as counts,domain FROM pantheon WHERE occupation='%s' GROUP BY domain ORDER BY counts DESC LIMIT 40" % (
        OCCUPATION)

    domain = get_mysql_data(query)

    query = "SELECT * FROM pantheon WHERE occupation='%s' ORDER BY HPI DESC LIMIT 40" % (
        OCCUPATION)

    people = get_mysql_data(query)
    return country, gender, domain, people


@app.route('/era', methods=["POST"])
def search_era():
    era = request.form.get("era", 1)
    print era
    query = "SELECT* FROM wiki_era WHERE id='%s'" % era
    country = get_mysql_data(query)[0]
    # print country
    start = country['start']
    end = country['end']
    continent = "%"
    place = "%"
    if (country['continent'] != "NA") & (country['continent'] != ''):
        continent = country['continent']

    if (country['country'] != "NA") & (country['country'] != ''):
        place = country['country']

    era = country

    country, gender, domain, occupation = search_era_stuff(start, end, continent, place)

    query = "SELECT id,wiki_key,title,start,end,country,continent FROM wiki_era"
    data = get_mysql_data(query)  # print response

    query = "SELECT id,occupation FROM pantheon GROUP BY occupation"
    occupations = get_mysql_data(query)

    return render_template('home.html', era=era, domain=domain, gender=gender, country=country,
                           occupation=occupation, list=data, occupations=occupations)


@app.route('/occupation', methods=["POST"])
def search_occupation():
    era = request.form.get("occupation", 1)

    country, gender, domain,people = search_occupation_stuff(era)

    query = "SELECT id,wiki_key,title,start,end,country,continent FROM wiki_era"
    data = get_mysql_data(query)  # print response

    query = "SELECT id,occupation FROM pantheon GROUP BY occupation"
    occupations = get_mysql_data(query)

    return render_template('occupation.html', era=era, domain=domain, gender=gender, country=country,people=people,
                           list=data, occupations=occupations)


@app.route('/search', methods=["GET"])
def hello_search_stuff():
    START = 1400
    END = 1700
    CONTINENT = "Europe"
    query = "SELECT COUNT(*) as counts,country FROM pantheon WHERE birthyear>'%s' AND birthyear<'%s' AND continent='%s' GROUP BY country ORDER BY counts DESC LIMIT 40" % (
        START, END, CONTINENT)

    country = get_mysql_data(query)

    query = "SELECT COUNT(*) as counts,gender FROM pantheon WHERE birthyear>'%s' AND birthyear<%s AND continent='%s' GROUP BY gender ORDER BY counts DESC LIMIT 40" % (
        START, END, CONTINENT)

    gender = get_mysql_data(query)

    query = "SELECT COUNT(*) as counts,domain FROM pantheon WHERE birthyear>%s AND birthyear<%s AND continent='%s' GROUP BY domain ORDER BY counts DESC LIMIT 40" % (
        START, END, CONTINENT)

    domain = get_mysql_data(query)

    query = "SELECT COUNT(*) as counts,occupation FROM pantheon WHERE birthyear>'%s' AND birthyear<%s AND continent='%s' GROUP BY occupation ORDER BY counts DESC LIMIT 20" % (
        START, END, CONTINENT)
    occupation = get_mysql_data(query)

    return render_template('home.html', domain=domain, gender=gender, country=country, occupation=occupation)


if __name__ == '__main__':
    app.run(debug=DEBUG, host="0.0.0.0")
"""" \
146	Persian_Empire	Persian Empires	-550	651

"""