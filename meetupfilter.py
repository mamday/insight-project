import sys
import nltk
from nltk import *
from sklearn.feature_extraction.text import CountVectorizer
from gensim import corpora, models, similarities
from gensim.models import word2vec
from sklearn import decomposition

#So, this is the script I used to initially test multiple different models to see exactly what I could use to try and filter my data by nerdiness
# For topic modeling I used LDA (latent dirichlet allocation), LSI (latent semantic indexing) and NNMF (non-negative matrix factorization). I found that when trained on the Meetup data that none of these methods really worked (all of them found topics like 'meetings' or 'days of the week'
#I then also tested using the word2vec algorithm, which is what I ultimately ended up using for my project

def main():
  in_file = sys.argv[1]
  imdb_model = word2vec.Word2Vec.load('/home/mamday/insight-project/300features_40minwords_10context')
  evt_list = []
  space_split_evt_list = []
  nerd_score = []
  evt_url = []
  for line in open(in_file).readlines():
    cur_split = line.split(',')
    if(cur_split[0]=="Event Info"):
      evt_url.append(cur_split[1])
    if(cur_split[0]=="Event Description"):
      cur_text =  ''.join(cur_split[1:])
      in_text = clean_text(cur_text)
      #print in_text
      evt_list.append(in_text)
      space_split_evt_list.append(in_text.split(' '))
      cur_score=0
      for word in (in_text.split(' ')):
        try:
          #print word
          cur_score+=(imdb_model.similarity('nerd',word))     
          #print 'Added'
        except:
          continue
      nerd_score.append(cur_score/len(in_text.split(' ')))
#LSI and LDA
  if(sys.argv[2]=='lsa'):
    evt_features,evt_vocab = GetVectors(evt_list)
    LSAModels(evt_features,evt_vocab)
#NNMF
  elif(sys.argv[2]=='nmf'):
    evt_features,evt_vocab = GetVectors(evt_list)
    NMFModels(evt_features,evt_vocab)
#word2vec
  elif(sys.argv[2]=='w2v'):
    try:
      w2v_model = word2vec.Word2Vec.load('/home/mamday/insight-project/meetupevents_500features_min20')
    except:
      w2v_model = W2VModels(space_split_evt_list)
    #corpus_list,w2v_list,v_dict = W2VtoCorpus(w2v_model,evt_list)
    #tfidf,tfidf_corpus = TFIDFModels(corpus_list)
    #print w2v_model.most_similar('nerd'),imdb_model.most_similar('nerd') 
    for i in xrange(len(evt_url)):
      #print len(evt_url),len(nerd_score),evt_url[:1],nerd_score[:10] 
      print i,',',evt_url[i],',',nerd_score[i]
  else:
     pass
#Algorithm that tokenizes, stems and lemmatizes words to make it easier to classify them
def clean_text(c_text,stop_bool=True,stem_bool=False,lem_bool=False):
  import re
  re_fit = re.sub("[^a-zA-Z]", " ", c_text).lower()
#Tokenize
  tok_first = nltk.word_tokenize(re_fit)
  slt_first=[] 
#Remove stop words
  if(stop_bool):
    stopwords = nltk.corpus.stopwords.words('english')
    slt_first = set([w for w in tok_first if not w in stopwords])
#Stem and Lemm
  elif(lem_bool):
    lem = nltk.WordNetLemmatizer()
    slt_first = set([lem.lemmatize(t) for t in slt_first])
  elif(stem_bool):
    mstem = nltk.LancasterStemmer()
    slt_first = set([mstem.stem(t) for t in slt_first])
  else:
    slt_first=tok_first

  return ' '.join(slt_first)

#Create a word2vec model from a corpus
def W2VModels(evt_list):
# Set values for various parameters
  num_features = 500 
  min_word_count = 20 
  num_workers = 4      
  context = 10                
  downsampling = 1e-3  

  print "Training model..."
  model = word2vec.Word2Vec(evt_list, workers=num_workers, \
            size=num_features, min_count = min_word_count, \
            window = context, sample = downsampling)

  model.init_sims(replace=True)
  model_name = "meetupevents_500features_min20"
  model.save(model_name)

  return model

#Create a corpus from word2vec vocabulary
def W2VtoCorpus(w2v_model,evt_list):
  v_dict = {}
  corpus_list = []
  w2v_list = []
  w2v_vocab = w2v_model.vocab
  for ind,key in enumerate(w2v_vocab.keys()):
    v_dict[key] = ind 

  for evt in evt_list:
    evt_words = evt.split(' ')   
    evt_vec = []
    evt_count = {}
    for word in evt_words:
      if(word in w2v_vocab):
        if(word in evt_count):
          evt_count[word]+=1
        else:
          evt_count[word]=1
    for word,w_count in evt_count.iteritems():
        w2v_list.append((v_dict[word],w2v_model[word]))
        evt_vec.append((v_dict[word],w_count))
    corpus_list.append(evt_vec)
  return corpus_list,w2v_list,v_dict

#Create a bag of words from a list of text (evt_list)
def GetVectors(evt_list,max_features=500):
  vectorizer = CountVectorizer(analyzer = "word",   \
                             tokenizer = None,    \
                             preprocessor = None, \
                             stop_words = None,   \
                             max_features = max_features) 
  in_features = vectorizer.fit_transform(evt_list)
  in_features = in_features.toarray()
  vocab = vectorizer.get_feature_names()
  vocab = numpy.array(vocab)
  return in_features,vocab

#Find topics using NNMF
def NMFModels(in_features,vocab):
  num_topics = 20
  num_top_words = 20
  clf = decomposition.NMF(n_components=num_topics, random_state=1)
  doctopic = clf.fit_transform(in_features)
  topic_words = []
  for topic in clf.components_:
        word_idx = numpy.argsort(topic)[::-1][0:num_top_words]
        topic_words.append([vocab[i] for i in word_idx])
  for t in range(len(topic_words)):
        print("Topic {}: {}".format(t, ' '.join(topic_words[t][:15])))

#Try to apply TFIDF to improve word weights and significance of topics
def TFIDFModels(corpus_list):
  tfidf = models.TfidfModel(corpus_list)
  tfidf_corpus = tfidf[corpus_list]
  return tfidf,tfidf_corpus

#Try to find topics with LSI and LDA
def LSAModels(in_features,vocab):
  corpus_list = []
  v_dict = {}
  for ind,item in enumerate(in_features):
    item_list = []
    for v_ind,val in enumerate(item):
      if(ind==0):
        v_dict[v_ind]=vocab[v_ind]
      if(val>0):
        item_list.append((v_ind,val))
    corpus_list.append(item_list)
  tfidf,tfidf_corpus = TFIDFModels(corpus_list)
  lsi_model = models.LsiModel(tfidf_corpus, id2word=v_dict, num_topics=10)
  lsi_out = lsi_model.print_topics(-1)
  print 'LSI',lsi_out
  lda_model = models.LdaModel(corpus_list, num_topics=10, id2word=v_dict, passes=4)
  lda_out = lda_model.print_topics(-1)
  print 'LDA',lda_out
  lda_model.print_topics(-1) 

if __name__=="__main__":
  main()
