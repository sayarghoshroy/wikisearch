# -*- coding: utf-8 -*-
"""index_maker.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1cWKqfUvhWwpXV-Yn6njrBB10r47HA9Zx
"""

import time
start = time.time();

import nltk
nltk.download('punkt')
import xml.sax
import subprocess
from copy import copy

import pickle
import sys
import re
import os
import shutil
# from nltk.tokenize.regexp import regexp_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from operator import itemgetter

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
  # tokens = regexp_tokenize(txt, pattern = '\s+', gaps = True)
  return tokens

# Example to show tokenization
# regtok("hello my name is {{Infobox a=100| anarchism|b=10| (hi) c = 900 | 2020 1st | }} 25th 2020 Sayar. Externallinks what is your name?")

# from google.colab import drive
# drive.mount('/content/gdrive')

# Template: https://towardsdatascience.com/wikipedia-data-science-working-with-the-worlds-largest-encyclopedia-c08efbac5f5c

'''
class WikiXmlHandler(xml.sax.handler.ContentHandler):
    """Content handler for Wiki XML data using SAX"""
    def __init__(self):
        xml.sax.handler.ContentHandler.__init__(self)
        self._buffer = None
        self._values = {}
        self._current_tag = None
        self._pages = []

    def characters(self, content):
        """Characters between opening and closing tags"""
        if self._current_tag:
            self._buffer.append(content)

    def startElement(self, name, attrs):
        """Opening tag of element"""
        if name in ('title', 'text'):
            self._current_tag = name
            self._buffer = []

    def endElement(self, name):
        """Closing tag of element"""
        if name == self._current_tag:
            self._values[name] = ' '.join(self._buffer)

        if name == 'page':
            self._pages.append((self._values['title'], self._values['text']))
'''

# title: 0, infobox: 1, body: 2, categories: 3, references: 4, external_links: 5

class NewHandler(xml.sax.ContentHandler):
	def __init__(self):
		xml.sax.ContentHandler.__init__(self)
		self.title_flag = False
		self.text_flag = False
		self.info_flag = False
		self.text_string = ""

	def startElement(self, name, attrs):
		global doc_id
		if name == "title":
			self.title_flag = True
		elif name == "text":
			self.text_flag = True
		elif name == "page":
			doc_id = doc_id + 1

	def endElement(self, name):
		global doc_id
		global indexed_dict
		global token_count

		info_tokens = []
		body_tokens = []
		link_tokens = []
		category_str = ""
		refer_str = ""
		body_flag = True
		link_flag = False
		info_flag = False

		if name == "text":
			self.text_flag = False
			tokens = regtok(self.text_string)
			
			categories_str = re.findall('(?<=\[\[category:)(.*?)(?=\]\])', self.text_string)
			ref_type_1 = re.findall('(?<=\* \[\[)(.*?)(?=\])', self.text_string)
			ref_type_2 = re.findall('(?<=\* \{\{)(.*?)(?=\}\})', self.text_string)

			category_tokens = []
			for stri in categories_str:
				all_tok = regtok(stri)
				for tok in all_tok:
					token_count += 1
					category_tokens.append(tok)

			refer_tokens = []
			for stri in ref_type_1:
				all_tok = regtok(stri)
				for tok in all_tok:
					token_count += 1	
					refer_tokens.append(tok)

			for stri in ref_type_2:
				all_tok = regtok(stri)
				for tok in all_tok:
					token_count += 1
					refer_tokens.append(tok)

			for token in tokens:
				token_count += 1
				if token == '{{infobox':
					info_flag = True
					body_flag = False
					continue

				if token == 'externallink':
					link_flag = True
					body_flag = False
					continue
				
				if info_flag is False and link_flag is False:
					body_flag = True
				
				if info_flag is True:
					if token == '}}':
						info_flag = False
						continue
					info_tokens.append(token)

				elif body_flag is True:
					body_tokens.append(token)
		 
				elif link_flag is True and info_flag is False:
					link_tokens.append(token)

			# Body
			for key in refer_tokens:
				if key not in indexed_dict:
					indexed_dict[key] = [[], [], [], [], [], [], [0, 0, 0, 0, 0, 0]]
				
				indexed_dict[key][6][4] += 1
				if not indexed_dict[key][4] or indexed_dict[key][4][-1] != doc_id:
					indexed_dict[key][4].append(doc_id)

			for key in category_tokens:
				if key not in indexed_dict:
					indexed_dict[key] = [[], [], [], [], [], [], [0, 0, 0, 0, 0, 0]]
				
				indexed_dict[key][6][3] += 1
				if not indexed_dict[key][3] or indexed_dict[key][3][-1] != doc_id:
					indexed_dict[key][3].append(doc_id)

			for key in body_tokens:
				if key not in indexed_dict:
					indexed_dict[key] = [[], [], [], [], [], [], [0, 0, 0, 0, 0, 0]]
				
				indexed_dict[key][6][2] += 1
				if not indexed_dict[key][2] or indexed_dict[key][2][-1] != doc_id:
					indexed_dict[key][2].append(doc_id)

			for key in link_tokens:
				if key not in indexed_dict:
					indexed_dict[key] = [[], [], [], [], [], [], [0, 0, 0, 0, 0, 0]]
				
				indexed_dict[key][6][5] += 1
				if not indexed_dict[key][5] or indexed_dict[key][5][-1] != doc_id:
					indexed_dict[key][5].append(doc_id)

			# Infobox

			for key in info_tokens:
				if key not in indexed_dict:
					indexed_dict[key] = [[], [], [], [], [], [], [0, 0, 0, 0, 0, 0]]
				
				indexed_dict[key][6][1] += 1
				if not indexed_dict[key][1] or indexed_dict[key][1][-1] != doc_id:
					indexed_dict[key][1].append(doc_id)

			self.text_string = ""

	def characters(self, data):
		global doc_id
		global indexed_dict
		global token_count

		if self.title_flag is True:
			data = data.replace(":", " ")
			tokens = regtok(data)
			
			for key in tokens:
				token_count += 1
				if key not in indexed_dict:
					indexed_dict[key] = [[], [], [], [], [], [], [0, 0, 0, 0, 0, 0]]
				
				indexed_dict[key][6][0] += 1
				if not indexed_dict[key][0] or indexed_dict[key][0][-1] != doc_id:
					indexed_dict[key][0].append(doc_id)
			
			self.title_flag = False

		if self.text_flag is True:
			self.text_string = self.text_string + " " + data.lower().replace("external links", "externallinks")

# data_path_zipped = './ph1.xml-p1p30303.bz2'
# # !bzip2 -d 'gdrive/My Drive/ph1.xml-p1p30303.bz2'
# data_path_unzipped = './ph1.xml-p1p30303'

data_path_unzipped = sys.argv[1]

cutoff = int(1e9)
handler = NewHandler()
parser = xml.sax.make_parser()
parser.setContentHandler(handler)

# For Running on the Zipped Version of the Dump:
# for line in subprocess.Popen(['bzcat'], stdin = open(data_path), stdout = subprocess.PIPE).stdout:
#     parser.feed(line)

#     if doc_id > cutoff:
#       break

# For Running on the UnZipped Dump:
# xml.sax.parse(data_path_unzipped, handler)

# file_handle = open(data_path_unzipped, 'r+')
# start_load = time.time()
# lines = file_handle.readlines()
# end_load = time.time()
# size = len(lines)

line = -1
doc_id = 0
count = 0

# while count < size:
with open(data_path_unzipped, "r+") as file_handle:
  while line != '':
      # Get next line from file 
      # line = lines[count]
      line = file_handle.readline()
      parser.feed(line)
      if doc_id > cutoff:
        break
      count += 1

OUTPUT_DIR = sys.argv[2]

if OUTPUT_DIR.endswith("/"):
	OUTPUT_DIR = OUTPUT_DIR[0: len(OUTPUT_DIR) - 1]

pickle_out = open(OUTPUT_DIR + "/index.pkl", "wb")
pickle.dump(indexed_dict, pickle_out)

end = time.time()

print("Number of Docs Processed =", doc_id)
print("Time Taken = " + str((end - start) / 60) + " minutes")
print("Token Count: " + str(token_count))

cnt = 0
for key in indexed_dict.keys():
  cnt += 1
print("Number of Keys: " + str(cnt))

# title: 0, infobox: 1, body: 2, categories: 3, references: 4, external_links: 5


# ^_^ Thank You