from flaskexample import app
from flask import render_template
from flask import request
from a_Model import ModelIt
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
import psycopg2

user = 'mamday' #add your username here (same as previous postgreSQL)                      
host = 'localhost'
dbname = 'meetup_db'
db = create_engine('postgres://%s%s/%s'%(user,host,dbname))
con = None
con = psycopg2.connect(database = dbname, user = user)

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html",
       title = 'Home', user = { 'nickname': 'Melanie' },
       )
'''
@app.route('/db')
def meetup_page():
    sql_query = """                                                                       
                SELECT * FROM event_table;          
                """
    query_results = pd.read_sql_query(sql_query,con)
    events = ""
    for i in range(0,10):
        events += query_results.iloc[i]['date']
        events += "<br>"
    return events

@app.route('/db_fancy')
def meetup_page_fancy():
    sql_query = """
               SELECT * FROM event_table;
                """
    query_results=pd.read_sql_query(sql_query,con)
    events = []
    for i in range(0,query_results.shape[0]):
        births.append(dict(index=query_results.iloc[i]['date'], attendant=query_results.iloc[i]['time'], birth_month=query_results.iloc[i]['fee']))
    return render_template('meetups.html',events=events)
'''
@app.route('/input')
def meetup_input():
    return render_template("input.html")

@app.route('/output')
def meetup_output():
  import numpy
  import geopy
  import time
  from geopy import *
  from geopy.distance import vincenty
  geolocator = Nominatim()

  user_add = request.args.get('address')
  user_date = request.args.get('date')
  user_time = request.args.get('time')
  in_loc = geolocator.geocode(user_add)
  in_latlon = (in_loc.latitude,in_loc.longitude)

  evt_query = "SELECT * FROM event_table"

  query_results=pd.read_sql_query(evt_query,con)

#Date and time
  evt_time = [str(i).strip() for i in query_results['date']]
  time_tostr = '%Y-%m-%d'
  epoch_time = numpy.array([time.mktime(time.strptime(i, time_tostr)) for i in evt_time])
  user_epoch_time = time.mktime(time.strptime(user_date, time_tostr)) 
  hours = numpy.array([int(i[1:3]) for i in query_results['time']])
  minutes = numpy.array([int(i[4:6]) for i in query_results['time']])
  user_hours = int(user_time[:2])
  user_minutes = int(user_time[3:])
  epoch_time = epoch_time+3600*hours+60*minutes
  user_epoch_time = user_epoch_time+3600*user_hours+60*user_minutes
  times = [(i-user_epoch_time) for i in epoch_time if (i-user_epoch_time)>0][:10]
  times.sort()

#Distance
  db_latlons = [i for i in zip(query_results["lat"],query_results["lon"])][:10]
  db_latlons.sort()
  the_result=''
  distances = [vincenty(in_latlon,j).kilometers for j in db_latlons]
  #the_result = ModelIt(stuff)
  return render_template("output.html", times=times, distances = distances, the_result = the_result)

