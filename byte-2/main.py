import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))
from flask import Flask, render_template

app = Flask(__name__)
from flask.ext.triangle import Triangle
Triangle(app)
API_KEY = "AIzaSyCfRmwMKY8NVG1YSP_bJzA44orhsZOtjmY"
TABLE_ID = "1HLka9ST2CZW9EE8kQkrw8FACWEttqFEqrzYPkf3N"
from apiclient.discovery import build
#https://www.google.com/fusiontables/data?docid=1HLka9ST2CZW9EE8kQkrw8FACWEttqFEqrzYPkf3N#rows:id=1
service = build('fusiontables', 'v1', developerKey=API_KEY)


#service = build('fusiontables', 'v1', developerKey=API_KEY)

#fp = open("data.json", "w+")
#json.dump(response, fp)

@app.route('/hello')
def hello_world():
    query = "SELECT * FROM " + TABLE_ID + " LIMIT 10"
    response = service.query().sql(sql=query).execute()
    return render_template('hello.html',response=response)

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
