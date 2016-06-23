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
from __future__ import division
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

nsim_gls = score_from_words(gnames,hn_model,nerd_vec)
nsim_els = score_from_words(enames,hn_model,nerd_vec)

#Write scores to pandable file
open('groupeventscores-1.csv','w')
f1.write('evt_id,g_score,e_score\n')
evts = {}

for ind in xrange(len(nsim_gls)):
    cur_e = query_results['evt_id'][ind]
    if(not(int(cur_e) in evts)):
        out_text = str(cur_e)+','+str(nsim_gls[ind])+','+str(nsim_els[ind])+'\n'
        f1.write(out_text)
    evts[int(cur_e)]=1


