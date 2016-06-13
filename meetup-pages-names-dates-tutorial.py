from __future__ import unicode_literals
from bs4 import BeautifulSoup
import requests
import urllib
import json
import time
import codecs
import sys
UTF8Writer = codecs.getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)


def main():
        api_key= open(sys.argv[1]).readlines()[0] 
        group_file = sys.argv[2]
        count = 0
        counted=False 
        for line in open(group_file).readlines():
          line = line.decode('unicode-escape') 
          cur_split = line.split(',')
          g_url = cur_split[9].rstrip()
          time.sleep(1)
          counted = event_from_url(api_key,g_url)  
          if(counted):
            count+=1
          time.sleep(1)
        print 'Matching Groups,',count

def get_groups(api_key):
        cities =[("Seattle","WA"),("Bellevue","WA"),("Redmond","WA")]
        #cities =[("Seattle","WA")]
        # Get your key here https://secure.meetup.com/meetup_api/key/
        for (city, state) in cities:
            per_page = 200
            results_we_got = per_page
            offset = 0
            while (results_we_got == per_page):
            #while (offset<2):
                # Meetup.com documentation here: http://www.meetup.com/meetup_api/docs/2/groups/
                response=get_results({"sign":"true","country":"US", "city":city, "state":state, "radius": 10, "key":api_key, "page":per_page, "offset":offset })
                time.sleep(1)
                offset += 1
                results_we_got = response['meta']['count']
                #tmp_count=0
                for group in response['results']:
                    tmp_count+=1
                    #print tmp_count,offset
                    #if(tmp_count>5):
                    #  break
                    category = ""
                    glink = ""
                    gdesc = ""
                    gnevent = ""
                    gcreated = ""
                    if "description" in group:
                        gdesc = BeautifulSoup(group['description'],"lxml").get_text()
                    if "created" in group:
                        gcreated = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(group['created']/1000))
                    if "link" in group:
                        glink = group['link'][group['link'].find('com/')+4:-1]
                    if "category" in group:
                        category = group['category']['name']
                    print "," .join(map(unicode, ['Group Info',city, group['name'].replace(","," "), gcreated, group['city'],group.get('state',""),category,group['members'], group.get('who',"").replace(","," "),glink]))
                    print 'Group Description,',gdesc
            time.sleep(1)

def event_from_url(api_key,glink,counted=False):
  try:
    e_response=get_results({'group_urlname':glink,'key':api_key},res='events')
  except:
    time.sleep(1800)
    try:
      e_response=get_results({'group_urlname':glink,'key':api_key},res='events')
    except:
      time.sleep(1800)
  if(e_response['meta']['count']>0):
    for event in e_response['results']:
      if(event['group']['join_mode']=='open' and event['status']=='upcoming' and event['visibility']=='public' and 'venue' in event and 'description' in event):
        counted=True
        e_fee = 0
        e_duration = -1 
        if('fee' in event):
          e_fee=event['fee']['amount'] 
        if('duration' in event):
          e_duration=(event['duration']/1000)/3600 
        print 'Event Description,',BeautifulSoup(event['description'],"lxml").get_text()
        print 'Event Info,',event['event_url'],',',event['name'],',',e_fee,',',e_duration,',',time.strftime('%Y-%m-%d, %H:%M:%S', time.localtime((event['time']/1000))),',',event['venue']['lat'],',',event['venue']['lon'] 
        print event['group'].keys(),event.keys()
  return counted



def get_results(params,res='groups'):
        ma_url = 'http://api.meetup.com/2/%s?' % (res)
        count=0
        for key,val in params.iteritems():
          count+=1
          if(count<(len(params))):
            ma_url+=str(key).rstrip()+'='+str(val).rstrip()+'&' 
          else:
            ma_url+=str(key).rstrip()+'='+str(val).rstrip() 
        #data = request.json()
        request=urllib.urlopen(ma_url)	
        data = json.loads(request.read())
	return data


if __name__=="__main__":
        main()


## Run this script and send it into a csv:
## python meetup-pages-names-dates.py > meetup_groups.csv
