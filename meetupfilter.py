import sys
import nltk
from nltk import *
from sklearn.feature_extraction.text import CountVectorizer
from gensim import corpora, models, similarities

in_file = sys.argv[1]


def clean_text(c_text):
  import re
  re_fit = re.sub("[^a-zA-Z]", " ", c_text).lower()
#Tokenize
  tok_first = nltk.word_tokenize(re_fit)
#Remove stop words
  stopwords = nltk.corpus.stopwords.words('english')
  slt_first = set([w for w in tok_first if not w in stopwords])
#Stem and Lemm
  lem = nltk.WordNetLemmatizer()
  sltl_first = set([lem.lemmatize(t) for t in slt_first])
  mstem = nltk.LancasterStemmer()
  sltls_first = set([mstem.stem(t) for t in sltl_first])

  return ' '.join(sltls_first)

def main():
  evt_list = []
  for line in open(in_file).readlines():
    cur_split = line.split(',')
    if(cur_split[0]=="Event Description"):
      cur_text =  ''.join(cur_split[1:])
      in_text = clean_text(cur_text)
      #print in_text
      evt_list.append(in_text)

  vectorizer = CountVectorizer(analyzer = "word",   \
                             tokenizer = None,    \
                             preprocessor = None, \
                             stop_words = None,   \
                             max_features = 500) 
  in_features = vectorizer.fit_transform(evt_list)
  in_features = in_features.toarray()
  vocab = vectorizer.get_feature_names()
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
  tfidf = models.TfidfModel(corpus_list)
  tfidf_corpus = tfidf[corpus_list]
  lsi_model = models.LsiModel(tfidf_corpus, id2word=v_dict, num_topics=100)
  lsi_out = lsi_model.print_topics(-1)
  print 'LSI',lsi_out
  lda_model = models.LdaModel(corpus_list, num_topics=100, id2word=v_dict, passes=4)
  lda_out = lda_model.print_topics(-1)
  print 'LDA',lda_out
  lda_model.print_topics(-1) 
if __name__=="__main__":
  main()
