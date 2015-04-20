import re

from BeautifulSoup import BeautifulSoup


__author__ = 'vikram'
import requests

URL = "http://en.m.wikipedia.org/wiki/List_of_time_periods"
IGNORE = ["Southeast Asia", "Philippines"]
KEYS = {"The Americas": {"country": "United States", "continentName": "North America"},
        "China": {"country": "China", "continentName": "Asia"},
        "Central Asia": {"country": "China", "continentName": "Asia"},
        "Africa": {"country": "Egypt", "continentName": "Africa"},
        "Europe": {"country": "Europe", "continentName": "Europe"},
        "India": {"country": "India", "continentName": "Asia"},
        "Japan": {"country": "Japan", "continentName": "Asia"},
        "Middle East": {"country": "Middle East", "continentName": "Asia"},
}
wiki = requests.get(URL)
# print wiki.text

regex = '<h3 class=\"in-block\">(.*)</h3>'
stuff = re.split(regex, wiki.text)
# print stuff[1]
filename = 'data.txt'
CROSS_WIN = "Crosses win"
NOUGHTS_WIN = "Noughts win"
DRAW = "Draw"
import MySQLdb

conn = MySQLdb.connect(host="localhost", user="root", passwd="worldpeace", db="pantheon")

WIKI_KEYS = ["wiki_key", "title", "start", "end", "meta", "country", "continent", "category_type",
             "error"]
WIKI_TABLE = "wiki_era"

def parse_date(date):
    keys = ["st ", "th "]
    for key in keys:
        date = date.replace(key, "00")

    date = date.replace(u'present', "2015")
    date = date.replace(u'Now', "2015")
    keys = ["century", "AD", " ", "after", "centuries"]
    for key in keys:
        date = date.replace(key, "")

    if "BC" in date:
        date = date.replace(u'BC', "")
        date = "-" + date

    re.sub(r'\W+', '', date)
    return date


def parse_numbers(text):
    # print text
    outer = re.compile("\((.*)\)")
    stuff = text
    text = outer.search(text)
    if text is not None:
        text = text.group(1)
    else:
        text = stuff
    city = ""

    if "," in text:
        home = text.split(",")[-1]
        city = text.split(",")[0]
        text = home

    kei = u'\u2013'
    text = text.replace(u'\u1ec7', kei)
    text = text.replace("-", kei)

    # print text.encode('latin-1')
    dates = text.split(kei)
    end = dates[0]
    if len(dates) > 1:
        end = dates[1]
    else:
        print text.encode('latin-1')
    return parse_date(dates[0]), parse_date(end), city


def parse_lis(key):
    soup = BeautifulSoup(key)
    link = "-"
    text = soup.find("li").getText(separator=u' ')
    if "), " in text:
        text = text.split(", ")[0]


    # print parse_numbers(text)
    # time = text.search("\((.*)\)")
    # print time
    if soup.find("a") is not None:
        # print soup.find("a")['href'],"---"
        link = soup.find("a")['href'].replace("/wiki/", "")
        # text = soup.find("a").text
    start, stop, city = parse_numbers(text)
    return link, text.split("(")[0].encode('latin-1', 'replace'), start, stop, city


def insert_wiki(data):
    game_data = []
    game_data.append(tuple(data))
    execute_many_sql(WIKI_TABLE, WIKI_KEYS, game_data)


def parse_li(text, country, continent, category="region"):
    regex = '<li>(.*)</li>'
    text = text.split("\n")
    # print text
    for key in text:
        if "<li>" in key:
            # print key
            stuff = list(parse_lis(key))
            cont = country
            if len(stuff[4]) > 3:
                cont = stuff[4]

            stuff.append(cont)
            stuff.append(continent)
            stuff.append(category)
            stuff.append(0)
            insert_wiki(stuff)
            print stuff

            # return


def execute_many_sql(table, keys, data):
    colums = ', '.join(keys)
    insert_sql = 'INSERT IGNORE INTO ' + table + ' (%s) values(%s)'
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


cur = conn.cursor()
states = []
game_data = []
k = 0
parse_li(stuff[4], "NA", "NA", "modern")

regex = '<h4 class=\"in-block\">(.*)</h4>'
stuff = re.split(regex, stuff[2])
soup = BeautifulSoup(wiki.text)
h4s = soup.findAll("h4")
i = 0
k = 0

for stuffs in stuff:


    if len(stuffs) > 250:


        index = max(i, 0)
        AGE = h4s[index].find("span").getText()
        if AGE not in IGNORE:
            print " ----------------------------"
            print " * "
            print KEYS[AGE]
            print " ----------------------------"
            print parse_li(stuffs, KEYS[AGE]['country'], KEYS[AGE]['continentName'])
            # print h4s[i].find("span").getText(separator=u' ')
            print " ----------------------------"

        else:
            print "Ignore"
            print h4s[index].find("span").getText()

        i += 1




        # print len(stuff)
        # print stuffs

        # print soup.findAll("h4")




