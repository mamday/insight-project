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
import time
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

#Filter words not in the corpus
def score_from_words(names,model):
  nsim_topic = []
  m_vocab = set(model.vocab)
  m_vocab.remove('seattle')
  for top in names:
    s_top = set(top)
    overlap = list(s_top & m_vocab)
    if(len(overlap)==0):
        nsim=-2
        nsim_topic.append(nsim)
        continue
    nsim = model.n_similarity(list(overlap),['nerd','geek','dork'])
    nan_bool = numpy.isnan(nsim)
    if(not(nan_bool)):
        nsim_topic.append(nsim)
    else:
        nsim=2
        nsim_topic.append(nsim)
  return nsim_topic

@app.route('/input')
def meetup_input():
    return render_template("input.html")

@app.route('/output')
def meetup_output():
  geolocator = Nominatim()

  imdb_model = word2vec.Word2Vec.load('/home/mamday/insight-project/300features_40minwords_10context')
  user_add = request.args.get('address')
  user_date = request.args.get('date')
  user_time = request.args.get('time')
  user_cost = request.args.get('cost')
  in_loc = geolocator.geocode(user_add)
  in_latlon = (in_loc.latitude,in_loc.longitude)

  evt_query = "SELECT * FROM event_table,group_table WHERE event_table.group_url=group_table.group_url AND event_table.fee<%s" % user_cost

  query_results=pd.read_sql_query(evt_query,con)
#Event web sites
  evt_urls = query_results['evt_url'] 

#Event and group names
  group_name = query_results['group_name']
  event_name = query_results['evt_name']
  gnames =[re.sub("[^a-zA-Z]", " ", i).lower().split(' ') for i in group_name]
  enames = [re.sub("[^a-zA-Z]", " ", i).lower().split(' ') for i in event_name]

  nsim_els = score_from_words(enames,imdb_model)
  nsim_gls = score_from_words(gnames,imdb_model)
 
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
  walk_time_dist_url_list = [(i,j,k,l,m,n) for i,j,k,l,m,n in zip(times,distances,evt_urls,nsim_els,nsim_gls,event_name) if j<1.7 and i>0 and (i+user_epoch_time)<(user_base_epoch_time+24*3600)]
  bike_time_dist_url_list = [(i,j,k,l,m,n) for i,j,k,l,m,n in zip(times,distances,evt_urls,nsim_els,nsim_gls,event_name) if j>1.7 and j<5 and i>0 and (i+user_epoch_time)<(user_base_epoch_time+24*3600)]
#Get url, distance and time of soonest events
  walkables = len(walk_time_dist_url_list)
  bikeables = len(bike_time_dist_url_list)
  the_result=''
  if(walkables==0 and bikeables==0):
    the_result='No walkable or bikeable events near you' 
  else:
#Sort by nerdiness of event name
    walk_time_dist_url_list.sort(key=lambda x: x[3],reverse=True)
    bike_time_dist_url_list.sort(key=lambda x: x[3],reverse=True)
#Keep top 10% most nerdy events, making sure to keep at least 1
    if(walkables>10):
      walk_time_dist_url_list = walk_time_dist_url_list[:(walkables/10)]
    if(bikeables>10):
      bike_time_dist_url_list = bike_time_dist_url_list[:(bikeables/10)]
#Sort by nerdiness of group name
    walk_time_dist_url_list.sort(key=lambda x: x[4],reverse=True)
    bike_time_dist_url_list.sort(key=lambda x: x[4],reverse=True)

#Sort by closest time to input time
#    walk_time_dist_url_list.sort()
#    bike_time_dist_url_list.sort()
    
    first_url=str(walk_time_dist_url_list[0][2]).strip()
    sec_url=str(bike_time_dist_url_list[0][2]).strip()
    first_name=str(walk_time_dist_url_list[0][5]).rstrip()
    sec_name=str(bike_time_dist_url_list[0][5]).rstrip()
    first_dist = walk_time_dist_url_list[0][1]
    first_dist = walk_time_dist_url_list[0][1]
    sec_dist = bike_time_dist_url_list[0][1]
    first_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(walk_time_dist_url_list[0][0]+user_epoch_time))
    sec_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(bike_time_dist_url_list[0][0]+user_epoch_time))
  if(the_result==''):
    return render_template("output.html", first_name=first_name,sec_name=sec_name,first_url=first_url, sec_url=sec_url,first_dist=first_dist,sec_dist=sec_dist,first_time=first_time,sec_time=sec_time)
  else:
#TODO: Figure out how to return an error page
    return
