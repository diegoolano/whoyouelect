import numpy as np
import lda
import lda.datasets
X = lda.datasets.load_reuters()
vocab = lda.datasets.load_reuters_vocab()
titles = lda.datasets.load_reuters_titles()

#print(X)
'''
[[1 0 1 ..., 0 0 0]
 [7 0 2 ..., 0 0 0]
 [0 0 0 ..., 0 0 0]
 ..., 
 [1 0 1 ..., 0 0 0]
 [1 0 1 ..., 0 0 0]
 [1 0 1 ..., 0 0 0]]
'''
#print(len(vocab))       #4258 set
#print len(titles)       #395  set


#print(X.shape)		#(395, 4258)
#print(X.sum())		#84010

#model = lda.LDA(n_topics=20, n_iter=1500, random_state=1)
#model.fit(X)  # model.fit_transform(X) is also available
#topic_word = model.topic_word_  # model.components_ also works
#n_top_words = 8
#for i, topic_dist in enumerate(topic_word):
#	topic_words = np.array(vocab)[np.argsort(topic_dist)][:-n_top_words:-1]
#	print('Topic {}: {}'.format(i, ' '.join(topic_words)))

'''
Topic 0: british churchill sale million major letters west
Topic 1: church government political country state people party
Topic 2: elvis king fans presley life concert young
Topic 3: yeltsin russian russia president kremlin moscow michael
Topic 4: pope vatican paul john surgery hospital pontiff
Topic 5: family funeral police miami versace cunanan city
Topic 6: simpson former years court president wife south
Topic 7: order mother successor election nuns church nirmala
Topic 8: charles prince diana royal king queen parker
Topic 9: film french france against bardot paris poster
Topic 10: germany german war nazi letter christian book
Topic 11: east peace prize award timor quebec belo
Topic 12: n't life show told very love television
Topic 13: years year time last church world people
Topic 14: mother teresa heart calcutta charity nun hospital
Topic 15: city salonika capital buddhist cultural vietnam byzantine
Topic 16: music tour opera singer israel people film
Topic 17: church catholic bernardin cardinal bishop wright death
Topic 18: harriman clinton u.s ambassador paris president churchill
Topic 19: city museum art exhibition century million churches

from pymongo import MongoClient
from __future__ import unicode_literals
from ftfy import fix_text
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters
import json
import sys
from functools import wraps
import errno
import os
import signal


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




######start here 
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
        sents = get_article_sentences(art)
        texts[a] = "\n".join(sents)


dbtexts = texts
print("Articles Used:",len(dbtexts.keys()))
print("Articles Skipped:",skipped)
'''


