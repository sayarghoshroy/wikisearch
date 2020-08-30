import pickle
import sys
import os

import nltk
nltk.download('punkt')
import re
import os
import shutil

from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer

stemmed_dict = {}

def stem(token):
  if token in stemmed_dict:
    return stemmed_dict[token]
  temp = snowball_stemmer.stem(token)
  stemmed_dict[token] = temp
  return temp

nltk.download('stopwords')
stopword = stopwords.words('english')
snowball_stemmer = SnowballStemmer('english')
word_set = {}

indexed_dict = {}
doc_id = 0

token_count = 0
for word in stopword:
  word_set[word] = None

def clean(txt):
  txt = txt.replace("\n", " ").replace("\r", " ")
  punc_list = '!"#$&*+,-./;?@\^_~)('
  t = str.maketrans(dict.fromkeys(punc_list, " "))
  txt = txt.translate(t)
  t = str.maketrans(dict.fromkeys("'`", ""))
  txt = txt.translate(t)

  return txt

def regtok(txt):
  txt = clean(txt)
  regex = re.compile(r'(\d+|\s+|=|}}|\|)')
  tokens = [stem(token) for token in regex.split(txt) if token not in word_set and (token.isalnum() or token == '}}' or token == '{{infobox')]
  return tokens

OUTPUT_DIR = sys.argv[1]

if OUTPUT_DIR.endswith("/"):
	OUTPUT_DIR = OUTPUT_DIR[0: len(OUTPUT_DIR) - 1]

pickle_in = open(OUTPUT_DIR + "/index.pkl", "rb")
index = pickle.load(pickle_in)

def stri(lst):
  N = len(lst)
  disp = min(N, 10)
  store = ""

  for i in range(disp):
    if i + 1 < disp:
      store = store + str(lst[i]) + ", "
    else:
      store = store + str(lst[i])
  
  if N > disp:
    store = store + ", ..."
  return store

def field_query(query):
  # t:World Cup i:2019 c:Cricket
  toks = regtok(query.lower().replace("t:", " ").replace("i:", " ").replace("r:", " ").replace("l:", " ").replace("b:", " ").replace("c:", " "))
  tokens = [stem(word) for word in toks if word not in word_set]

  print()

  for token in tokens:
    if token not in index:
      print("Token: " + str(token) + " NOT FOUND")
      continue
    
    print("Stem: " + str(token))
    print("Counts:")
    print("Title: " + str(index[token][6][0]) + ", Infobox: " + str(index[token][6][1]) + ", Categories: " + str(index[token][6][3]) + ", References: " + str(index[token][6][4]) + ", Body: " + str(index[token][6][2]) + ", Links: " + str(index[token][6][5]))
    print("Postings:")
    print("Title: " + stri(index[token][0]))
    print("Infobox: " + stri(index[token][1]))
    print("Categories: " + stri(index[token][3]))
    print("References: " + stri(index[token][4]))
    print("Body: " + stri(index[token][2]))
    print("Links: " + stri(index[token][5]))
    print()

  return

query = sys.argv[2]
field_query(query)
