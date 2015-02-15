from datetime import date, datetime
import json
import os
import sys
import simplejson

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))
from flask import Flask, render_template

app = Flask(__name__)
from flask.ext.triangle import Triangle
import dateutil.parser

Triangle(app)
API_KEY = "AIzaSyCfRmwMKY8NVG1YSP_bJzA44orhsZOtjmY"
TABLE_ID = "1HLka9ST2CZW9EE8kQkrw8FACWEttqFEqrzYPkf3N"
from apiclient.discovery import build
# https://www.google.com/fusiontables/data?docid=1HLka9ST2CZW9EE8kQkrw8FACWEttqFEqrzYPkf3N#rows:id=1
service = build('fusiontables', 'v1', developerKey=API_KEY)


# service = build('fusiontables', 'v1', developerKey=API_KEY)

#fp = open("data.json", "w+")
#json.dump(response, fp)

@app.route('/hello')
def hello_world():
    data = get_all_data()
    columns = data['columns']
    #print columns
    rows = data['rows']
    outcome_date = columns.index(u'OutcomeDate')
    outcome_month = columns.index(u'OutcomeMonth')
    intake_date = columns.index(u'Intake Date')
    sex = columns.index(u'Sex')
    animal_type = columns.index(u'Animal Type')
    color = columns.index(u'Color')
    estimated_age = columns.index(u'Estimated Age')

    #data_dic = {"days":{},"months":{}}
    keys = {"days","months","animal","color","sex","estimated_age"}
    data_dic = {}
    for key in keys:
        data_dic[key] ={}


    for row in rows:
        #print row,outcome_date

        diff = days_between(row[outcome_date], row[intake_date])
        fill_data(data_dic['days'],diff)
        fill_data(data_dic['months'],row[outcome_month])
        fill_data(data_dic['animal'],row[animal_type])
        fill_data(data_dic['color'],row[color])
        fill_data(data_dic['sex'],row[sex])
        fill_data(data_dic['estimated_age'],row[estimated_age])

    for key in data_dic:
        new_data = dict((k, v) for k, v in (data_dic[key].iteritems()) if v>15)
        #data_dic[key] = sorted(new_data.items(), key=lambda x: x[1])
        data_dic[key] = new_data

    return render_template('hello.html', response=json.dumps(data_dic),data=data_dic)

def get_all_data():
        """ collect data from the server. """

        # open the data stored in a file called "data.json"
        try:
            fp = open("data/data.json")
            response = simplejson.load(fp)
        # but if that file does not exist, download the data from fusiontables
        except IOError:

            service = build('fusiontables', 'v1', developerKey=API_KEY)
            query = "SELECT * FROM " + TABLE_ID + " WHERE 'Outcome Type' = 'Returned to Owner' AND 'Zip Where Found' >1 "
            response = service.query().sql(sql=query).execute()
            with open('data/data.json', 'w') as outfile:
                json.dump(response, outfile)


        return response

def fill_data(field,column):
    column = column if column!='' else "other"
    if column in field:
            field[column]+= 1
    else:
            field[column] = 1


def days_between(d1, d2):
    d1 = dateutil.parser.parse(d1)
    d2 = dateutil.parser.parse(d2)
    return abs((d2 - d1).days)


@app.route('/')
def home():
    data = get_all_data()
    columns = data['columns']
    #print columns
    rows = data['rows']
    outcome_date = columns.index(u'OutcomeDate')
    outcome_month = columns.index(u'OutcomeMonth')
    intake_date = columns.index(u'Intake Date')
    sex = columns.index(u'Sex')
    animal_type = columns.index(u'Animal Type')
    color = columns.index(u'Color')
    estimated_age = columns.index(u'Estimated Age')

    #data_dic = {"days":{},"months":{}}
    keys = {"days","months","animal","color","sex","estimated_age"}
    data_dic = {}
    for key in keys:
        data_dic[key] ={}


    for row in rows:
        #print row,outcome_date

        diff = days_between(row[outcome_date], row[intake_date])
        fill_data(data_dic['days'],diff)
        fill_data(data_dic['months'],row[outcome_month])
        fill_data(data_dic['animal'],row[animal_type])
        fill_data(data_dic['color'],row[color])
        fill_data(data_dic['sex'],row[sex])
        fill_data(data_dic['estimated_age'],row[estimated_age])

    for key in data_dic:
        new_data = dict((k, v) for k, v in (data_dic[key].iteritems()) if v>15)
        #data_dic[key] = sorted(new_data.items(), key=lambda x: x[1])
        data_dic[key] = new_data
    return render_template('home.html',response=json.dumps(data_dic),data=data_dic)


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)
