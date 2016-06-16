
# coding: utf-8

# In[1]:

from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2
import pandas as pd
import sys

dbname = 'meetup_db'
username = 'mamday'
pswd = 'gr8ndm8'

engine = create_engine('postgresql://%s:%s@localhost/%s'%(username,pswd,dbname))

if not database_exists(engine.url):
    create_database(engine.url)

# connect:
con = None
con = psycopg2.connect(database = dbname, user = username, host='localhost', password=pswd)




# In[18]:

# Group Url join queries
sql_query = """
SELECT * FROM event_table WHERE group_url='seattleworldmusic';
"""
gurl_from_table = pd.read_sql_query(sql_query,con)

print 'Event',gurl_from_table[:2]

#Get all from wild card - Super useful
#sql_query = """
#SELECT * FROM group_table WHERE group_url LIKE '%seattleworldmusic%';
#"""

sql_query = """
SELECT * FROM group_table WHERE group_url='seattleworldmusic';
"""
gurl_from_table = pd.read_sql_query(sql_query,con)
print 'Group',gurl_from_table[:2]

sql_query = """
SELECT * FROM event_table, group_table WHERE event_table.group_url=group_table.group_url;
"""

joingurl_from_table = pd.read_sql_query(sql_query,con)
print 'Joined',joingurl_from_table[:2]


# In[34]:

# Evt ID join queries
sql_query = """
SELECT * FROM event_table WHERE evt_id='22';
"""
evtid_from_table = pd.read_sql_query(sql_query,con)

print 'Event',evtid_from_table[:2]

sql_query = """
SELECT * FROM search_table WHERE evt_id='22';
"""
evtid_from_table = pd.read_sql_query(sql_query,con)

print 'Search',evtid_from_table[:2]

sql_query = """
SELECT search_table.evt_url FROM event_table,search_table WHERE event_table.evt_id=search_table.evt_id;
"""
evtid_from_table = pd.read_sql_query(sql_query,con)
print 'Join',evtid_from_table["evt_url"][:2]


# In[70]:

#Test that I can do things with the values that I expect to be able to do
sql_query = """
SELECT nerd_score,evt_id FROM search_table;
"""
nerdscore_from_table = pd.read_sql_query(sql_query,con)
#print 3*nerdscore_from_table[nerdscore_from_table<0][:2],3*nerdscore_from_table[nerdscore_from_table>0][:2]
print 3*nerdscore_from_table["nerd_score"][nerdscore_from_table["nerd_score"]>0.1][:2]

sql_query = """
SELECT date,evt_id FROM event_table;
"""
date_from_table = pd.read_sql_query(sql_query,con)
print date_from_table['date'][0][1:5],date_from_table['date'][0][6:8],date_from_table['date'][0][9:11]

sql_query = """
SELECT time,evt_id FROM event_table;
"""
time_from_table = pd.read_sql_query(sql_query,con)
print time_from_table['time'][0][1:3],time_from_table['time'][0][4:6]

sql_query = """
SELECT fee,evt_id FROM event_table;
"""
fee_from_table = pd.read_sql_query(sql_query,con)
print 3*fee_from_table["fee"][fee_from_table["fee"]>0][:2]

sql_query = """
SELECT lat,evt_id FROM event_table;
"""
lat_from_table = pd.read_sql_query(sql_query,con)
print 3*lat_from_table["lat"][:2],lat_from_table["lat"][lat_from_table["lat"]<0][:2]

sql_query = """
SELECT lon,evt_id FROM event_table;
"""
lon_from_table = pd.read_sql_query(sql_query,con)
print 3*lon_from_table["lon"][:2],lon_from_table["lon"][lon_from_table["lon"]<0][:2]


# In[ ]:



