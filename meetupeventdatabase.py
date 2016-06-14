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

# load a database from CSV
meetup_data = pd.DataFrame.from_csv('seattle_pandas.csv')
meetup_data["fee"] = [float(i) for i in meetup_data['fee']]
meetup_data["duration"] = [float(i) for i in meetup_data['duration']]
meetup_data["lat"] = [float(i) for i in meetup_data['lat']]
meetup_data["lon"] = [float(i) for i in meetup_data['lon']]
meetup_data["group_url"] = [i[i.find('com/')+4:i.find('/events')] for i in meetup_data["evt_url"]]
cnx = engine.raw_connection()
meetup_data.to_sql('event_table', engine, if_exists='replace')

# connect:
con = None
con = psycopg2.connect(database = dbname, user = username, host='localhost', password=pswd)

# query:
sql_query = """
SELECT * FROM event_table WHERE fee>0;
"""
fee_from_table = pd.read_sql_query(sql_query,con)

fee_from_table.head()

