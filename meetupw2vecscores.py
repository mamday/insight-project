from __future__ import division
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2
import pandas as pd
import numpy
import sys
import time
import geopy 
from geopy import *
from geopy.distance import vincenty
from gensim import corpora, models, similarities
from gensim.models import word2vec
import re

#Get cosine similarity of constructed vector pmvec and list of words vec2
def cos_sim(pmvec,vec2):
    pmvec = pmvec/numpy.sqrt(sum(pmvec*pmvec))
    return sum(pmvec*norm_vec(vec2))

#Normalize the length of the vector to 1
def norm_vec(vec_text):
    vec = 300*[0]
    for v in vec_text:
        vec+=hn_model[v]
    return vec/numpy.sqrt(sum(vec*vec))

#Get the nerd score, either using the word2vec score (cs_score=False) or my method, which used the vector n_vec to produce a nerd vector that can have both vector addition and subtraction (cs_score=True). Also filters out words not in the corpus since they cannot be scored
def score_from_words(names,model,n_vec,cs_score=True):
  nsim_topic = []
  m_vocab = [m.decode('utf-8') for m in model.vocab]
  m_vocab = set(m_vocab)
  try:
    m_vocab.remove('seattle')
  except:  
    pass
  nsim=0
  for top in names:
    s_top = set(top)
    overlap = list(s_top & m_vocab)
    if(len(overlap)==0):
        nsim=-2
        nsim_topic.append(nsim)
        continue
    if(cs_score):
      nsim = cos_sim(n_vec,list(overlap))
    else:
      nsim = model.n_similarity(['nerd','geek','dork'],list(overlap))

    #print overlap,nsim
    nan_bool = numpy.isnan(nsim)
    if(not(nan_bool)):
        nsim_topic.append(nsim)
    else:
        nsim=2
        nsim_topic.append(nsim)
  return nsim_topic

#Load Hacker News corpus
hn_model = word2vec.Word2Vec.load('/home/mamday/insight-project/HN_300features_40minwords_10context')

nerd_vec =(hn_model['nerd']+hn_model['geek']+hn_model['activity']+hn_model['hobby']-2*hn_model['person'])

#Very simple postgres database validation information I do not care enough about to save in a special secret text file
dbname = 'meetup_db'
username = 'mamday'
pswd = 'gr8ndm8'

# connect to postgres database
engine = create_engine('postgresql://%s:%s@localhost/%s'%(username,pswd,dbname))

if not database_exists(engine.url):
    create_database(engine.url)

con = None
con = psycopg2.connect(database = dbname, user = username, host='localhost', password=pswd)

user_cost=100

import nltk
from nltk.corpus import stopwords
#Query that includes only events that cost less than user_cost
evt_query = "SELECT * FROM event_table,group_table WHERE event_table.group_url=group_table.group_url AND event_table.fee<%s" % user_cost
query_results=pd.read_sql_query(evt_query,con)

group_topic = query_results['topic']
group_name = query_results['group_name']
event_name = query_results['evt_name']

#Produce easy lookup sets to access topics and stop words
topics = set(group_topic)
stops = set(stopwords.words("english"))
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

#Tokenize group names, event names and topics and remove stop words
gnames = [[tokenizer.tokenize(w)[0] for w in re.sub("[^a-zA-Z]", " ", i).lower().split() if not(w in stops)] for i in group_name]
enames = [[tokenizer.tokenize(w)[0] for w in re.sub("[^a-zA-Z]", " ", i).lower().split() if not(w in stops)] for i in event_name]
tnames=[[tokenizer.tokenize(w)[0] for w in re.sub("[^a-zA-Z]", " ", i).lower().split() if not(w in stops)] for i in group_topic]

#Use cleaned words to get 'nerd score' for group names and event names. Get result for both word2vec method of calculating similarity and also with my own method (which allows me to add or subtract some other words)
nsim_gls = score_from_words(gnames,hn_model,nerd_vec,False)
nsim_els = score_from_words(enames,hn_model,nerd_vec,False)
nnsim_els = score_from_words(enames,hn_model,nerd_vec)


#Write scores to pandable file
def write_scores(query,my_nsim_gls,my_nsim_els,my_nnsim_els,file_name='groupeventscores-1.csv'):
  f1 = open(file_name,'w')
  f1.write('evt_id,g_score,e_score\n')
  evts = {}

  for ind in xrange(len(my_nsim_gls)):
    cur_e = query['evt_id'][ind]
    if(not(int(cur_e) in evts)):
        out_text = str(cur_e)+','+str(my_nsim_gls[ind])+','+str(my_nsim_els[ind])+','+str(my_nnsim_els)+'\n'
        f1.write(out_text)
    evts[int(cur_e)]=1

#write_scores(query_result,nsim_gls,nsim_els,nnsim_els)
