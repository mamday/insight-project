from flaskexample import app
from flask import render_template
from flask import request
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
import psycopg2
import re
import numpy
import geopy
import random,sys,time
from geopy import *
from geopy.distance import vincenty

user = 'mamday' #add your username here (same as previous postgreSQL)                      
#host = 'localhost'
host = '127.0.0.1'
dbname = 'meetup_db'
db = create_engine('postgres://%s%s/%s'%(user,host,dbname))
con = None
con = psycopg2.connect(database = dbname, user = user)

def get_stars(score):
  if(score<0.165):
    return '1 Star'
  elif(score>=0.165 and score<0.221):
    return '2 Star'
  elif(score>=0.221 and score<0.277):
    return '3 Star'
  elif(score>=0.277 and score<0.329):
    return '4 Star'
  elif(score>=0.329):
    return '5 Star'

@app.route('/')
@app.route('/index')
def run():
    return render_template("index.html",
       )

#@app.route('/about')
#def run():
#    return render_template("about.html",
#       )

@app.route('/input')
def meetup_input():
    return render_template("input.html")


@app.route('/output')
def meetup_output():
  geolocator = Nominatim()

  user_add = request.args.get('address')
  user_date = request.args.get('date')
#  user_time = request.args.get('time')
  user_cost = request.args.get('cost')
  the_result=''
  try:
    in_loc = geolocator.geocode(user_add,timeout=None)
    in_latlon = (in_loc.latitude,in_loc.longitude)
  except:
    the_result = 'Your address is invalid'
    return render_template("nooutput.html",the_result=the_result)
  try:
    float(user_cost)
    evt_query = "SELECT * FROM event_table,newsearch_table WHERE event_table.evt_id=newsearch_table.evt_id AND event_table.fee<=%s AND newsearch_table.e_score>0" % user_cost
  except:
    the_result='Cost input is invalid'
    return render_template("nooutput.html",the_result=the_result)
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
  user_base_epoch_time = -1
  try:
    user_base_epoch_time = time.mktime(time.strptime(user_date, time_tostr)) 
  except: 
    the_result='Date input is invalid'
    return render_template("nooutput.html",the_result=the_result)
  hours = numpy.array([int(i[1:3]) for i in query_results['time']])
  minutes = numpy.array([int(i[4:6]) for i in query_results['time']])
  #user_hours = int(user_time[:2])
  #user_minutes = int(user_time[3:])
  epoch_time = epoch_time+3600*hours+60*minutes
  user_epoch_time = user_base_epoch_time
  times = [(i-user_epoch_time) for i in epoch_time]

#Distance
  db_latlons = zip(query_results["lat"],query_results["lon"])
  distances = [vincenty(in_latlon,j).kilometers for j in db_latlons]

#Get times for walkable and bikeable distances on the input day
  walk_time_dist_url_list = set([(i,j,k,l,m,n,o) for i,j,k,l,m,n,o in zip(times,distances,evt_urls,nsim_els,nsim_gls,event_name,db_latlons) if j<1.7 and i>0 and (i+user_epoch_time)<(user_base_epoch_time+24*3600)])
  bike_time_dist_url_list = set([(i,j,k,l,m,n,o) for i,j,k,l,m,n,o in zip(times,distances,evt_urls,nsim_els,nsim_gls,event_name,db_latlons) if j>1.7 and j<5 and i>0 and (i+user_epoch_time)<(user_base_epoch_time+24*3600)])
  walk_time_dist_url_list = list(walk_time_dist_url_list)
  bike_time_dist_url_list = list(bike_time_dist_url_list)
  walk_time_dist_url_list.sort(key=lambda x: x[4],reverse=True)
  bike_time_dist_url_list.sort(key=lambda x: x[4],reverse=True)
#  walk_time_dist_url_list.sort(key=lambda x: x[3])
#  bike_time_dist_url_list.sort(key=lambda x: x[3])
  walk_time_dist_url_list = walk_time_dist_url_list[:10]
  bike_time_dist_url_list = bike_time_dist_url_list[:10]
  print 'Groups',len(walk_time_dist_url_list),len(bike_time_dist_url_list)
  walk_time_dist_url_list.sort(key=lambda x: x[3],reverse=True)
  bike_time_dist_url_list.sort(key=lambda x: x[3],reverse=True)
  walk_time_dist_url_list = walk_time_dist_url_list[:5]
  bike_time_dist_url_list = bike_time_dist_url_list[:5]
#Map the events
  import branca,folium
  map_osm = folium.Map(location=[in_latlon[0],in_latlon[1]],zoom_start=12,width=500,height=500)
  #map_osm.simple_marker([in_latlon[0],in_latlon[1]], popup='Your Location',marker_color='red')
  icon = folium.Icon(color='red',icon='home',prefix='fa')
  folium.Marker([in_latlon[0],in_latlon[1]], icon=icon).add_to(map_osm)

#Get url, distance and time of soonest events
  walkables = len(walk_time_dist_url_list)
  bikeables = len(bike_time_dist_url_list)
  print 'Result:',walkables,bikeables 
  if(walkables==0 and bikeables==0):
    the_result='No walkable or bikeable events matching your criteria' 
    return render_template("nooutput.html",the_result=the_result)
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
    walk_urls = []
    walk_names = []
    walk_dists = []
    walk_times = []
    walk_stars = []

    bike_urls = []
    bike_names = []
    bike_dists = []
    bike_times = []
    bike_stars = []
    if(walkables>0):
      #rand_walk = random.choice(walk_time_dist_url_list)
      for w in walk_time_dist_url_list:
        print 'Walk',w[3]
        #print w
        cur_stars = get_stars(w[3])
        walk_stars.append(get_stars(w[3]))
        walk_urls.append(str(w[2]).strip())
        cur_url=str(w[2]).strip()
        first_name=str(w[5]).rstrip()
        cur_name=first_name.decode('utf-8')
        walk_names.append(first_name.decode('utf-8'))
        walk_dists.append('%.2f' % w[1]) 
        cur_dist='%.2f' % w[1]
        walk_times.append(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(w[0]+user_epoch_time)))
        cur_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(w[0]+user_epoch_time))

        marker_html="""<p>"""+cur_stars+"""-</p>"""+"""<a href=""" + cur_url+""">"""+cur_name+"""</a><p>at """ +cur_time+ """, within """ +cur_dist+""" kilometers.</p>""" 
        iframe = branca.element.IFrame(html=marker_html, width=300, height=50)
        popup = folium.Popup(iframe)
        icon = folium.Icon(color='blue',icon='blind',prefix='fa')
        folium.Marker([w[6][0],w[6][1]], popup=popup,icon=icon).add_to(map_osm)
    else:
      first_url='www.meetup.com'
      first_name='No events'
      first_dist = '0' 
      first_time = '24:00' 

    if(bikeables>0):
      #rand_bike = random.choice(bike_time_dist_url_list)
      for b in bike_time_dist_url_list:
        print 'Bike',b[3]
        cur_stars = get_stars(b[3])
        bike_stars.append(get_stars(b[3]))
        cur_url = str(b[2]).strip()
        bike_urls.append(str(b[2]).strip())
        sec_name = str(b[5]).rstrip()
        cur_name=sec_name.decode('utf-8')
        bike_names.append(sec_name.decode('utf-8'))
        cur_dist='%.2f' % b[1]
        bike_dists.append('%.2f' % b[1])
        cur_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(b[0]+user_epoch_time))
        bike_times.append(time.strftime('%Y-%m-%d, %H:%M:%S', time.localtime(b[0]+user_epoch_time)))

        marker_html="""<p>"""+cur_stars+"""-</p>"""+"""<a href=""" + cur_url+""">"""+cur_name+"""</a><p>at """ +cur_time+ """, within """ +cur_dist+""" kilometers.</p>""" 
        #marker_html="""
        #<a href=""" + cur_url+""">"""+cur_name+"""</a><p>at """ +cur_time+ """, within """ +cur_dist+""" kilometers.</p>
        #""" 
        icon = folium.Icon(color='green',icon='bicycle',prefix='fa')
        iframe = branca.element.IFrame(html=marker_html, width=300, height=50)
        popup = folium.Popup(iframe)
        folium.Marker([b[6][0],b[6][1]], popup=popup,icon=icon).add_to(map_osm)
    else:
      sec_url='www.meetup.com'
      sec_name='No events'
      sec_dist = '0' 
      sec_time = '24:00' 

  folium.TileLayer('cartodbdark_matter').add_to(map_osm)
  tmp_rand = random.choice(xrange(1,99999))
  map_osm.create_map(path='flaskexample/templates/osm-%s.html' % (tmp_rand))

  if(the_result==''):
    #return render_template("output.html", first_name=first_name,sec_name=sec_name,first_url=first_url, sec_url=sec_url,first_dist=first_dist,sec_dist=sec_dist,first_time=first_time,sec_time=sec_time)
    return render_template("output.html", tmp_rand=tmp_rand, walk_stars=walk_stars,bike_stars=bike_stars, walkables=walkables,bikeables=bikeables,walk_urls=walk_urls,bike_urls=bike_urls,walk_names=walk_names,bike_names=bike_names,walk_dists=walk_dists,bike_dists=bike_dists,walk_times=walk_times,bike_times=bike_times)
  else:
# Should never happen now
    return render_template("nooutput.html",the_result=the_result)
