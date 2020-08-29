import time
start = time.time();

import nltk
nltk.download('punkt')
import xml.sax
import subprocess
from copy import copy

import tqdm
import pickle
import sys
import re
import os
import shutil
from collections import defaultdict
from nltk.tokenize.regexp import regexp_tokenize
from collections import Counter
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from nltk.stem import PorterStemmer
from operator import itemgetter

def clean(txt):
  txt = txt.replace("\n", " ").replace("\r", " ")
  punc_list = '!"#$&*+,-./;?@\^_~0123456789'
  t = str.maketrans(dict.fromkeys(punc_list, " "))
  txt = txt.translate(t)
  t = str.maketrans(dict.fromkeys("'`", ""))
  txt = txt.translate(t)

  return txt

def regtok(txt):
  txt = clean(txt)
  tokens = regexp_tokenize(txt, pattern = '\s+', gaps = True)
  return tokens

start = time.time()

# Template: https://towardsdatascience.com/wikipedia-data-science-working-with-the-worlds-largest-encyclopedia-c08efbac5f5c

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

nltk.download('stopwords')

stopword = stopwords.words('english')
snowball_stemmer = SnowballStemmer('english')

indexed_dict = {}
doc_id = 0
# output_path = sys.argv[2]

stemmed_dict = {}

def stem(token):
  if token in stemmed_dict:
    return stemmed_dict[token]
  temp = snowball_stemmer.stem(token)
  stemmed_dict[token] = temp
  return temp

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
		global stopword
		global doc_id
		global indexed_dict
		global output_path
		global index_number

		info_tokens = []
		body_tokens = []
		link_tokens = []
		match_curl = []
		category_str = ""
		refer_str = ""
		info_flag = False
		equal_flag = False
		n_flag = False
		body_flag = True
		link_flag = False

		if name == "text":
			self.text_flag = False

			# tokens = word_tokenize(self.text_string.replace("External links", "Externallinks"))#.split(" ")
			tokens = regtok(self.text_string.replace("External links", "Externallinks"))
			cat_str = re.findall('(?<=\[\[category:)(.*?)(?=\]\])', self.text_string)
			ref_str_1 = re.findall('(?<=\* \[\[)(.*?)(?=\])', self.text_string)
			ref_str_2 = re.findall('(?<=\* \{\{)(.*?)(?=\}\})', self.text_string)

			category_tokens = []
			for stri in cat_str:
				if stri != '':
					category_tokens.append(stri.replace(")", "").replace("(", "").strip())

			refer_tokens = []
			for stri in ref_str_1:
				temp = stri.replace(")", "").replace("(", "").strip()
				if temp.isalpha():	
					refer_tokens.append(temp)

			for stri in ref_str_2:
				temp = stri.replace(")", "").replace("(", "").strip()
				if temp.isalpha():	
					refer_tokens.append(temp)

			for token in tokens:
				if token == '{{infobox':
					info_flag = True
					body_flag = False

				if token == 'externallinks':
					link_flag = True
					body_flag = False
				
				if info_flag is False and link_flag is False:
					body_flag = True
				
				if info_flag is True:
					if token == '}}' and n_flag is True:
						info_flag = False
					if n_flag is True:
						n_flag = False
					if token == '\n':
						n_flag = True
					if token == '|':
						equal_flag = False
					if equal_flag is True:
						info_tokens.append(token)
					if token == '=':
						equal_flag = True

				if body_flag is True:
					body_tokens.append(token.replace(")", "").replace("(", ""))
		 
				if link_flag is True and info_flag is False:
					link_tokens.append(token.replace(")", "").replace("(", ""))

			# Body
			refer_tokens = [stem(word) for word in refer_tokens if word.isalpha() and word not in stopword]
			
			for key in refer_tokens:
				if key not in indexed_dict:
					indexed_dict[key] = [[], [], [], [], [], [], [0, 0, 0, 0, 0, 0]]
				
				indexed_dict[key][6][4] += 1
				if not indexed_dict[key][4] or indexed_dict[key][4][-1] != doc_id:
					indexed_dict[key][4].append(doc_id)

			category_tokens = [stem(word).strip() for word in category_tokens if word.isalpha() and word not in stopword]

			for key in category_tokens:
				if key not in indexed_dict:
					indexed_dict[key] = [[], [], [], [], [], [], [0, 0, 0, 0, 0, 0]]
				
				indexed_dict[key][6][3] += 1
				if not indexed_dict[key][3] or indexed_dict[key][3][-1] != doc_id:
					indexed_dict[key][3].append(doc_id)
		
			body_tokens = [stem(word).strip() for word in body_tokens if word.isalpha() and word not in stopword]

			for key in body_tokens:
				if key not in indexed_dict:
					indexed_dict[key] = [[], [], [], [], [], [], [0, 0, 0, 0, 0, 0]]
				
				indexed_dict[key][6][2] += 1
				if not indexed_dict[key][2] or indexed_dict[key][2][-1] != doc_id:
					indexed_dict[key][2].append(doc_id)
		
			link_tokens = [stem(word).strip() for word in link_tokens if word.isalpha() and word not in stopword]

			for key in link_tokens:
				if key not in indexed_dict:
					indexed_dict[key] = [[], [], [], [], [], [], [0, 0, 0, 0, 0, 0]]
				
				indexed_dict[key][6][5] += 1
				if not indexed_dict[key][5] or indexed_dict[key][5][-1] != doc_id:
					indexed_dict[key][5].append(doc_id)

			# Infobox
			info_tokens = [stem(word).strip() for word in info_tokens if word.isalpha() and word not in stopword]

			for key in info_tokens:
				if key not in indexed_dict:
					indexed_dict[key] = [[], [], [], [], [], [], [0, 0, 0, 0, 0, 0]]
				
				indexed_dict[key][6][1] += 1
				if not indexed_dict[key][1] or indexed_dict[key][1][-1] != doc_id:
					indexed_dict[key][1].append(doc_id)

			self.text_string = ""

	def characters(self, data):
		global stopword
		global doc_id
		global indexed_dict

		if self.title_flag is True:
			data = data.lower().replace(")", "").replace("(", "").replace(":", " ")
			# tokens = word_tokenize(data)#.split(" ")
			tokens = regtok(data)

			tokens = [stem(word).strip() for word in tokens if word.isalpha() and word not in stopword]
			
			for key in tokens:
				if key not in indexed_dict:
					indexed_dict[key] = [[], [], [], [], [], [], [0, 0, 0, 0, 0, 0]]
				
				indexed_dict[key][6][0] += 1
				if not indexed_dict[key][0] or indexed_dict[key][0][-1] != doc_id:
					indexed_dict[key][0].append(doc_id)
			
			self.title_flag = False

		if self.text_flag is True:
			data = data.replace("External links", "Externallinks").lower()
			self.text_string = self.text_string + " " + data

	def characters(self, data):
		global stopword
		global doc_id
		global indexed_dict

		if self.title_flag is True:
			data = data.lower().replace(")", "").replace("(", "").replace(":", " ")
			tokens = data.split(" ")

			tokens = [stem(word) for word in tokens if word.isalpha() and word not in stopword]
			
			for key in tokens:
				if key not in indexed_dict:
					indexed_dict[key] = [[], [], [], [], [], [], [0, 0, 0, 0, 0, 0]]
				
				indexed_dict[key][6][0] += 1
				if not indexed_dict[key][0] or indexed_dict[key][0][-1] != doc_id:
					indexed_dict[key][0].append(doc_id)
			
			self.title_flag = False

		if self.text_flag is True:
			data = data.replace("External links", "Externallinks").lower()
			self.text_string = self.text_string + " " + data

data_path_zipped = './ph1.xml-p1p30303.bz2'
# !bzip2 -d 'gdrive/My Drive/ph1.xml-p1p30303.bz2'
data_path_unzipped = './ph1.xml-p1p30303'

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

file_handle = open(data_path_unzipped, 'r+')
start_load = time.time()
# lines = file_handle.readlines()
end_load = time.time()
# size = len(lines)
doc_id = 0
count = 0
line = -1

# while count < size:
while line != '': 
    # Get next line from file
    # line = lines[count]
    line = file_handle.readline()
    parser.feed(line)
    if doc_id > cutoff:
      break
    count += 1

pickle_out = open("index.pkl", "wb")
pickle.dump(indexed_dict, pickle_out)

end = time.time()

print("Number of Docs Processed =", doc_id)
print("Time Taken = " + str((end - start) / 60) + " minutes")
print("Load Time = " + str((end_load - start_load) / 60) + " minutes")

cnt = 0
for key in indexed_dict.keys():
  cnt += 1
  if cnt < 2:
    print(str(key) + ": " + str(indexed_dict[key]))

print(str((end - start) / 60) + " minutes")
cnt = 0
for key in indexed_dict.keys():
  cnt += 1
print("Number of Keys: " + str(cnt))

# ^_^ Thank You
