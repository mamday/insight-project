from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2
import pandas as pd
import sys

def main():
  dbname = 'meetup_db'
  username = 'mamday'
  pswd = 'gr8ndm8'
  engine = init_db(username,pswd,dbname)
# connect:
  con = None
  con = psycopg2.connect(database = dbname, user = username, host='localhost', password=pswd)
  if(sys.argv[1]=='event'):
    load_event_csv(engine)
    test_evt_query(dbname,username,pswd,con)
  if(sys.argv[1]=='group'):
    load_group_csv(engine)
    test_group_query(dbname,username,pswd,con)
  if(sys.argv[1]=='search'):
    load_search_csv(engine)
    test_search_query(dbname,username,pswd,con)
  if(sys.argv[1]=='none'):
    pass

def init_db(username,pswd,dbname):
  engine = create_engine('postgresql://%s:%s@localhost/%s'%(username,pswd,dbname))

  if not database_exists(engine.url):
    create_database(engine.url)
  return engine 

def load_event_csv(engine):
  # load a database from CSV
  meetup_data = pd.DataFrame.from_csv(sys.argv[2])
  meetup_data["fee"] = [float(i) for i in meetup_data['fee']]
  meetup_data["duration"] = [float(i) for i in meetup_data['duration']]
  meetup_data["lat"] = [float(i) for i in meetup_data['lat']]
  meetup_data["lon"] = [float(i) for i in meetup_data['lon']]
  meetup_data["group_url"] = [i[i.find('com/')+4:i.find('/events')] for i in meetup_data["evt_url"]]
  cnx = engine.raw_connection()
  meetup_data.to_sql('newevent_table', engine, if_exists='replace')

def load_group_csv(engine):
  meetup_data = pd.DataFrame.from_csv(sys.argv[2])
  cnx = engine.raw_connection()
  meetup_data.to_sql('group_table', engine, if_exists='replace')

def load_search_csv(engine):
  meetup_data = pd.DataFrame.from_csv(sys.argv[2])
  meetup_data["g_score"] = [float(i) for i in meetup_data["g_score"]]
  meetup_data["e_score"] = [float(i) for i in meetup_data["e_score"]]
  meetup_data["h_score"] = [float(i) for i in meetup_data["h_score"]]
  meetup_data["s_score"] = [float(i) for i in meetup_data["s_score"]]
  cnx = engine.raw_connection()
  meetup_data.to_sql('newsearch_table', engine, if_exists='replace')


def test_evt_query(dbname,username,pswd,con):
# query:
  sql_query = """
  SELECT * FROM newevent_table WHERE fee>0;
  """
  fee_from_table = pd.read_sql_query(sql_query,con)

  print fee_from_table[:10]

def test_group_query(dbname,username,pswd,con):
# query:
  sql_query = """
  SELECT * FROM group_table WHERE topic='tech';
  """
  topic_from_table = pd.read_sql_query(sql_query,con)

  print topic_from_table[:10]

def test_search_query(dbname,username,pswd,con):
# query:
  sql_query = """
  SELECT * FROM newsearch_table WHERE g_score>0.33;
  """
  nscore_from_table = pd.read_sql_query(sql_query,con)
  print nscore_from_table[:100]

if __name__=="__main__":
  main()
