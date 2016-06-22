from flaskexample import app
from flask import render_template
from flask import request
from a_Model import ModelIt
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
import psycopg2
import re
from gensim import corpora, models, similarities
from gensim.models import word2vec
import numpy
import geopy
import random,sys,time
from geopy import *
from geopy.distance import vincenty

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
       title = 'Home', user = { 'nickname': 'Magnificent Melanie' },
       )

@app.route('/input')
def meetup_input():
    return render_template("input.html")

@app.route('/output')
def meetup_output():
  geolocator = Nominatim()

  user_add = request.args.get('address')
  user_date = request.args.get('date')
  user_time = request.args.get('time')
  user_cost = request.args.get('cost')
  in_loc = geolocator.geocode(user_add,timeout=None)
  in_latlon = (in_loc.latitude,in_loc.longitude)

  evt_query = "SELECT * FROM event_table,newsearch_table WHERE event_table.evt_id=newsearch_table.evt_id AND event_table.fee<%s AND (newsearch_table.g_score>0.33 OR newsearch_table.e_score>0.29)" % user_cost

  query_results=pd.read_sql_query(evt_query,con)
#Event web sites
  evt_urls = query_results['evt_url'] 
  print len(evt_urls)
#Event and group names
  event_name = query_results['evt_name']
  nsim_els = query_results['e_score']
  nsim_gls = query_results['g_score']
 
#Date and time
  evt_time = [str(i).strip() for i in query_results['date']]
  time_tostr = '%Y-%m-%d'
  epoch_time = numpy.array([time.mktime(time.strptime(i, time_tostr)) for i in evt_time])
  user_base_epoch_time = time.mktime(time.strptime(user_date, time_tostr)) 
  hours = numpy.array([int(i[1:3]) for i in query_results['time']])
  minutes = numpy.array([int(i[4:6]) for i in query_results['time']])
  user_hours = int(user_time[:2])
  user_minutes = int(user_time[3:])
  epoch_time = epoch_time+3600*hours+60*minutes
  user_epoch_time = user_base_epoch_time+3600*user_hours+60*user_minutes
  times = [(i-user_epoch_time) for i in epoch_time]

#Distance
  db_latlons = zip(query_results["lat"],query_results["lon"])
  distances = [vincenty(in_latlon,j).kilometers for j in db_latlons]

#Get times for walkable and bikeable distances on the input day
  walk_time_dist_url_list = [(i,j,k,l,m,n,o) for i,j,k,l,m,n,o in zip(times,distances,evt_urls,nsim_els,nsim_gls,event_name,db_latlons) if j<1.7 and i>0 and (i+user_epoch_time)<(user_base_epoch_time+24*3600)]
  bike_time_dist_url_list = [(i,j,k,l,m,n,o) for i,j,k,l,m,n,o in zip(times,distances,evt_urls,nsim_els,nsim_gls,event_name,db_latlons) if j>1.7 and j<5 and i>0 and (i+user_epoch_time)<(user_base_epoch_time+24*3600)]

#Map the events
  import folium
  map_osm = folium.Map(location=[in_latlon[0],in_latlon[1]],zoom_start=12,width=500,height=500)
  map_osm.simple_marker([in_latlon[0],in_latlon[1]], popup='Your Location',marker_color='red')

#Get url, distance and time of soonest events
  walkables = len(walk_time_dist_url_list)
  bikeables = len(bike_time_dist_url_list)
  print 'Result:',walkables,bikeables 
  the_result=''
  if(walkables==0 and bikeables==0):
    the_result='No walkable or bikeable events near you' 
  else:
#Sort by nerdiness of group name
    #walk_time_dist_url_list.sort(key=lambda x: x[4],reverse=True)
    #bike_time_dist_url_list.sort(key=lambda x: x[4],reverse=True)
#Keep top 10% most nerdy events, making sure to keep at least 1
    #if(walkables>10):
    #  walk_time_dist_url_list = walk_time_dist_url_list[:(walkables/10)]
    #if(bikeables>10):
    #  bike_time_dist_url_list = bike_time_dist_url_list[:(bikeables/10)]
#Sort by nerdiness of event name
    #walk_time_dist_url_list.sort(key=lambda x: x[3],reverse=True)
    #bike_time_dist_url_list.sort(key=lambda x: x[3],reverse=True)
    if(walkables>0):
      rand_walk = random.choice(walk_time_dist_url_list)
      #map_osm.simple_marker([walk_time_dist_url_list[0][6][0],walk_time_dist_url_list[0][6][1]], popup='Walking Distance')
      map_osm.simple_marker([rand_walk[6][0],rand_walk[6][1]], popup='Walking Distance')
      first_url=str(rand_walk[2]).strip()
      first_name=str(rand_walk[5]).rstrip()
      first_name=first_name.decode('utf-8')
      first_dist = '%.3f' % rand_walk[1] 
      first_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(rand_walk[0]+user_epoch_time))
    else:
      first_url='www.meetup.com'
      first_name='No events'
      first_dist = '0' 
      first_time = '24:00' 

    if(bikeables>0):
      rand_bike = random.choice(bike_time_dist_url_list)
      map_osm.simple_marker([rand_bike[6][0],rand_bike[6][1]], popup='Biking Distance',marker_color='green')
      sec_url=str(rand_bike[2]).strip()
      sec_name=str(rand_bike[5]).rstrip()
      sec_name=sec_name.decode('utf-8')
      sec_dist = '%.3f' % rand_bike[1]
      sec_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(rand_bike[0]+user_epoch_time))
    else:
      sec_url='www.meetup.com'
      sec_name='No events'
      sec_dist = '0' 
      sec_time = '24:00' 

  folium.TileLayer('cartodbdark_matter').add_to(map_osm)
  map_osm.create_map(path='flaskexample/templates/osm.html')

  if(the_result==''):
    return render_template("output.html", first_name=first_name,sec_name=sec_name,first_url=first_url, sec_url=sec_url,first_dist=first_dist,sec_dist=sec_dist,first_time=first_time,sec_time=sec_time)
  else:
#TODO: Figure out how to return an error page
    return
