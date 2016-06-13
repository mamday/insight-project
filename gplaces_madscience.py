import sys,urllib, json
import geopy
from geopy import *

# Input at commond line: python gplaces_madscience.py [keyfile] [outputfile] [searchtype] [activitytype] 

my_key = open(sys.argv[1]).readlines()[0]

def LatLongFromText(location):
  geolocator = Nominatim()
  coded_location = geolocator.geocode("Seattle, Washington")
  return (coded_location.latitude, coded_location.longitude)

#Grabbing and parsing the JSON data
def GoogPlace(search,lat,lng,radius,types,key,token=None):
  #making the url
  SEARCH = search
  AUTH_KEY = key
  LOCATION = str(lat) + "," + str(lng)
  RADIUS = radius
  TYPES = types
  TOKEN=token
  if(token==None):
    MyUrl = ('https://maps.googleapis.com/maps/api/place/%s/json'
           '?location=%s'
           '&radius=%s'
           '&types=%s'
           '&sensor=false&key=%s'
           '&rsz=20') % (SEARCH, LOCATION, RADIUS, TYPES, AUTH_KEY)
  else:
    MyUrl = ('https://maps.googleapis.com/maps/api/place/%s/json'
           '?location=%s'
           '&radius=%s'
           '&types=%s'
           '&sensor=false&key=%s'
           '&pagetoken=%s') % (SEARCH, LOCATION, RADIUS, TYPES, AUTH_KEY,TOKEN)

  #grabbing the JSON result
  response = urllib.urlopen(MyUrl)
  jsonRaw = response.read()
  jsonData = json.loads(jsonRaw)
  return jsonData

def GetPlace(loc_text,search_type,act_type,token=None):
#Get location from text name of city
  loc = LatLongFromText(loc_text)
#Get query in json format
  place = GoogPlace(search_type,loc[0],loc[1],30000,act_type,'AIzaSyAUxpl83drKarqdupn-xN3i-pR0_TFFlcA',token)
  return place
#Example 'radarsearch'
cur_search = sys.argv[3] 
#Example 'restaurant'
act_type=sys.argv[4]

#Get data from the API 
place = GetPlace("Seattle, Washington",cur_search,act_type)

#Write out the information
json.dump(place,open(sys.argv[2],'w'))

#Keep fetching information if it exists
try:
  next_token = place['next_page_token']
  cur_iter+=1
  place = GetPlace("Seattle, Washington",cur_search,act_type,next_token)
  json.dump(place,open(sys.argv[2][:sys.argv[2].find('.json')]+'-'+cur_iter+'.json','w'))
except:
  print 'Not more next tokens'

