import requests

__author__ = 'vikram'
import MySQLdb

def get_wiki_abstract(stuff):
    url = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro=&explaintext=&titles=%s"%stuff
    wiki = requests.get(url)
    if wiki.status_code ==200:
        try:
            #print wiki.json()['query']['pages'].itervalues().next()['extract']
            return  unicode(wiki.json()['query']['pages'].itervalues().next()['extract'].encode("utf-8"), "utf-8")
        except Exception as e:
            print e
            print "error"
    return ""

def update_sql(data,id):
    print data,id
    SQL = "UPDATE wiki_era SET abstract=%s WHERE id=%s "
    cur.execute(
        SQL,
        (data,id))
    id = conn.insert_id()
    print id
    conn.commit()


conn = MySQLdb.connect(host="localhost", user="root", passwd="worldpeace", db="pantheon")
db = conn
db.set_character_set('utf8')
cur = conn.cursor()
dbc = cur
dbc.execute('SET NAMES utf8;')
dbc.execute('SET CHARACTER SET utf8;')
dbc.execute('SET character_set_connection=utf8;')

sql = "SELECT id,wiki_key FROM wiki_era WHERE wiki_key!=''"
cur = conn.cursor()
cur.execute(sql)
data = cur.fetchall()
for row in data:
    print row
    update_sql(get_wiki_abstract(row[1]),int(row[0]))



