from __future__ import unicode_literals
from ftfy import fix_text
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters
import json
import sys
from functools import wraps
import errno
import os
import signal
from pymongo import MongoClient

import nltk
import string
import os
import sys

#https://github.com/mneedham/neo4j-qcon/blob/master/topics.py
import csv

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF
from collections import defaultdict
#from bs4 import BeautifulSoup, NavigableString
#from soupselect import select

def uri_to_file_name(uri):
    return uri.replace("/", "-")
###

import datetime
from dateutil.parser import *
import traceback
def handle_date(art):
	success = 0
	try:
		if 'date' not in art:
			if 'time' in art:
				date_text = art['time']
				dt = parse(date_text)	
				ntime = dt.strftime("%Y-%m-%d")
				art['date'] = ntime
				del art['time']
				success = 1
			else:
				print("ERROR couldn't find 'date' or 'time' in article:")
				print(art)
		else:
			date_text = art['date']
			dt = parse(date_text)	
			ntime = dt.strftime("%Y-%m-%d")
			art['date'] = ntime
			success = 1
			
	except:
		try:
			years = range(2000,2015) 
			for y in years:
				if str(y) in art["url"]:
					pos = art["url"].index(str(y))
					posend = pos + 1
					while posend < len(art["url"]):
						try:
							x = int(art["url"][posend])
							posend = posend + 1
						except:
							date_text = art["url"][pos:posend]
							dt = parse(date_text)
							ntime = dt.strftime("%Y-%m-%d")
							art['date'] = ntime
							if 'time' in art: del art['time']
							success = 1
							print("NEWDATE: "+date_text)
							break
					break
			if success == 0:
				#print("In HANDLE DATE WITH ART: "+art["url"]+" .. BAD DATE FORMAT IN JSON SO LOOK IN URL FOR A DATE OR JUST GIVE IT A DUMMY DATE")    #Abel Herrero 59,68,75,124,125
				#still no luck so default to dummy date of 2000-01-01
				dt = parse("2000-01-01")
				ntime = dt.strftime("%Y-%m-%d")
				art['date'] = ntime 
				if 'time' in art: del art['time']
				print("NEWDATE: DEFAULT: 2000-01-01")
				success = 1
		except:
			print("STILL COULDNT HANDLE DATE SO SKIP ARTICLE")
			traceback.print_exc(file=sys.stdout)
				
			

	return [success,art]


def get_article_sentences(article): 
    subs = {'Sen.':'Senator','Lt. Gov.':'Lieutenant Governor','Rep.':'Representative','Reps.':'Representatives,', 'Gov.':'Governor'}

    if 'body' in article:
        text = fix_text(article['body']).replace('?"', '? "').replace('!"', '! "').replace('."', '. "')
        for a in subs:
            text = text.replace(a,subs[a])
            sentences = sentence_splitter.tokenize(text)
        return sentences
    elif 'text' in article:
        text = fix_text(article['text']).replace('?"', '? "').replace('!"', '! "').replace('."', '. "')
        for a in subs:
            text = text.replace(a,subs[a])
            sentences = sentence_splitter.tokenize(text)
        return sentences
    return []


conn = MongoClient()
db = conn.newsdb   #db is called "newsdb"

punkt_param = PunktParameters()
sentence_splitter = PunktSentenceTokenizer(punkt_param)

name = "Eddie Rodriguez"
results = db.texnews.english.find({"entity":name},timeout=False)

texts = {}
skipped = 0
for a,art in enumerate(results):
    if a > -1:
        if "/sports/" in art["url"]:
            skipped += 1
            continue

	success,art = handle_date(art)
	arts = "\n".join(get_article_sentences(art))
	tt = arts.lower().translate({ord(c): None for c in string.punctuation})
	narts = tt.encode('ascii','ignore').replace("\n"," ")

        sents = {'abstract': narts, 'title':art['title']}    #for use with python solution!

	#title = art['title'].encode('ascii','ignore').replace("\n"," ")
        #sents = {'text': narts, 'url':art['url'], 'title':title, 'news-source':art['news-source'], 'date': art['date'], 'language': art['language']}    #for use to write to file for R solution
	
        #texts[a] = "\n".join(sents)
        texts[a] = sents


dbtexts = texts
print("Articles Used:",len(dbtexts.keys()))
print("Articles Skipped:",skipped)


#WRITE OUT TO FILE as a tsv for R
'''
topline = "title\tdate\tsource\turl\tlanguage\ttext\n"
for i in texts:
	a = texts[i]	
	topline += a['title']+"\t"+a['date']+"\t"+a['news-source']+"\t"+a['url']+"\t"+a['language']+"\t"+a['text']+"\n"

with open("eddie_rodriguez-articles.tsv",'wb') as tsvfile:
	tsvfile.write(topline)

sys.exit()
'''

'''
sessions = {}
with open("data/sessions.csv", "r") as sessions_file:
    reader = csv.reader(sessions_file, delimiter = ",")
    reader.next() # header
    for row in reader:
        session_id = int(row[0])
        filename = "data/sessions/" + uri_to_file_name(row[4])
        page = open(filename).read()
        soup = BeautifulSoup(page)
        abstract = select(soup, "div.brenham-main-content p")
        if abstract:
            sessions[session_id] = {"abstract" : abstract[0].text, "title": row[3] }
        else:
            abstract = select(soup, "div.pane-content p")
            sessions[session_id] = {"abstract" : abstract[0].text, "title": row[3] }
'''
sessions = texts


corpus = []
titles = []
for id, session in sorted(sessions.iteritems(), key=lambda t: int(t[0])):
    corpus.append(session["abstract"])
    titles.append(session["title"])




n_topics = 15
n_top_words = 50
n_features = 6000

# vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1,1), min_df = 0, stop_words = 'english')
vectorizer = CountVectorizer(analyzer='word', ngram_range=(1,1), min_df = 0, stop_words = 'english')
matrix =  vectorizer.fit_transform(corpus)
feature_names = vectorizer.get_feature_names()

import lda
import numpy as np

vocab = feature_names

model = lda.LDA(n_topics=20, n_iter=500, random_state=1)
model.fit(matrix)
topic_word = model.topic_word_
n_top_words = 20

for i, topic_dist in enumerate(topic_word):
    topic_words = np.array(vocab)[np.argsort(topic_dist)][:-n_top_words:-1]
    print('Topic {}: {}'.format(i, ' '.join(topic_words)))

doc_topic = model.doc_topic_
for i in range(0, len(titles)):
    print("{} (top topic: {})".format(titles[i], doc_topic[i].argmax()))
    print(doc_topic[i].argsort()[::-1][:3])

# with open("data/topics.csv", "w") as file:
#     writer = csv.writer(file, delimiter=",")
#     writer.writerow(["topicId", "word"])
#
#     for i, topic_dist in enumerate(topic_word):
#         topic_words = np.array(vocab)[np.argsort(topic_dist)][:-n_top_words:-1]
#         for topic_word in topic_words:
#             writer.writerow([i, topic_word])
#         print('Topic {}: {}'.format(i, ' '.join(topic_words)))
#
# with open("data/sessions-topics.csv", "w") as file:
#     writer = csv.writer(file, delimiter=",")
#     writer.writerow(["sessionId", "topicId"])
#
#     doc_topic = model.doc_topic_
#     for i in range(0, len(titles)):
#         writer.writerow([i, doc_topic[i].argmax()])
#         print("{} (top topic: {})".format(titles[i], doc_topic[i].argmax()))
#         print(doc_topic[i].argsort()[::-1][:3])
