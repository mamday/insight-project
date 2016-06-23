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

#Filter words not in the corpus
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


hn_model = word2vec.Word2Vec.load('/home/mamday/insight-project/HN_300features_40minwords_10context')

nerd_vec =(hn_model['nerd']+hn_model['geek']+hn_model['activity']+hn_model['hobby']-2*hn_model['person'])

geolocator = Nominatim()

dbname = 'meetup_db'
username = 'mamday'
pswd = 'gr8ndm8'

engine = create_engine('postgresql://%s:%s@localhost/%s'%(username,pswd,dbname))

if not database_exists(engine.url):
    create_database(engine.url)

# connect:
con = None
con = psycopg2.connect(database = dbname, user = username, host='localhost', password=pswd)

user_cost=100
import nltk
from nltk.corpus import stopwords
evt_query = "SELECT * FROM event_table,group_table WHERE event_table.group_url=group_table.group_url AND event_table.fee<%s" % user_cost
query_results=pd.read_sql_query(evt_query,con)

#group_topic = [clean_text(i,stop_bool=False).split(' ') for i in query_results['topic']]
group_topic = query_results['topic']
group_name = query_results['group_name']
event_name = query_results['evt_name']

topics = set(group_topic)
stops = set(stopwords.words("english"))
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

gnames = [[tokenizer.tokenize(w)[0] for w in re.sub("[^a-zA-Z]", " ", i).lower().split() if not(w in stops)] for i in group_name]
enames = [[tokenizer.tokenize(w)[0] for w in re.sub("[^a-zA-Z]", " ", i).lower().split() if not(w in stops)] for i in event_name]
tnames=[[tokenizer.tokenize(w)[0] for w in re.sub("[^a-zA-Z]", " ", i).lower().split() if not(w in stops)] for i in group_topic]

nsim_gls = score_from_words(gnames,hn_model,nerd_vec,False)
nsim_els = score_from_words(enames,hn_model,nerd_vec,False)
nnsim_els = score_from_words(enames,hn_model,nerd_vec)

print len(nsim_gls),len(nsim_els),len(nnsim_els),nsim_gls[:10],nsim_els[:10],nnsim_els[:10]

#Write scores to pandable file

#f1 = open('groupeventscores-1.csv','w')
#f1.write('evt_id,g_score,e_score\n')
#evts = {}

#for ind in xrange(len(nsim_gls)):
#    cur_e = query_results['evt_id'][ind]
#    if(not(int(cur_e) in evts)):
#        out_text = str(cur_e)+','+str(nsim_gls[ind])+','+str(nsim_els[ind])+','+str(nnsim_els)+'\n'
#        f1.write(out_text)
#    evts[int(cur_e)]=1


