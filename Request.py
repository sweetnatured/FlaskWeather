import weakref
import requests
import time, threading
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from datetime import datetime , timedelta

print(datetime.now())

app = Flask (__name__)
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.sqlite3'

db = SQLAlchemy(app)

class weather(db.Model):
   
   id = db.Column(db.Integer, primary_key=True) 
   city = db.Column(db.String(30))
   weather = db.Column(db.Integer)
   time = db.Column(db.DateTime , default= datetime.now() )
   
   def repr(self):
     return " %s, %s" %(self.city , self.weather)

db.create_all()

current_time = datetime.utcnow()
two_days_ago = current_time - timedelta(hours=48)

if len(sys.argv) == 2:

    def fetch_data():       
       try:
           response = requests.get("https://wttr.in/{}?format=j1".format(sys.argv[1]))
           res_json = response.json()
       except:
           raise Exception("Couldn't connect to the API ")
     
       current_weather = res_json['current_condition'][0]['temp_C']
       city_weather = weather(city= sys.argv[1] , weather = current_weather)
       db.session.add(city_weather)
       db.session.commit()
  
       print(current_weather)
       print(db.session.query(weather.weather).filter(weather.city == sys.argv[1]).all())


       threading.Timer(1200, fetch_data).start()
       
    fetch_data()

else:
    raise Exception("Please enter the city that you want to search")
      


@app.route('/', methods=['GET'])
def current():
    return "<h1> Current degree of {} is {} </h1>".format(sys.argv[1], weather.query.all()[-1].weather)

@app.route('/Max', methods=['GET'])
def max():
    return "<h1>Max degree of {} is  {} </h1>".format(sys.argv[1], db.session.query(func.max(weather.weather)).filter(weather.time >  two_days_ago , weather.city == sys.argv[1] ).scalar())

@app.route('/Min', methods=['GET'])
def min():
    return "<h1>Min degree of {} is  {} </h1>".format(sys.argv[1], db.session.query(func.min(weather.weather)).filter( weather.time > two_days_ago , weather.city == sys.argv[1] ).scalar())    

@app.route('/Avg', methods=['GET'])
def avg():
    return "<h1>Avg degree is of {} is  {} </h1>".format(sys.argv[1], db.session.query(func.avg(weather.weather)).filter(weather.time > two_days_ago , weather.city == sys.argv[1] ).scalar())


app.run()    