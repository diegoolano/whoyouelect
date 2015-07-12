from langdetect import detect, detect_langs
import sys, os
import json
import datetime
from pymongo import MongoClient
from elasticsearch import Elasticsearch

def add_houstonchronicle(db,searchfor):
	houston_path = "/Users/dolano/htdocs/dama-larca/data/" + searchfor
	houston_dirs = ["sh1", "sh2","sh3","sh4","sh5"]
	c = 0
	es_cnt = 0
	en_cnt = 0
	for coma in houston_dirs:
	    print coma+" - "
	    cur = 0
	    for root, subFolders, files in os.walk(os.path.join(houston_path,coma)):    
		if subFolders == []:          
		    if len(os.listdir(root)) > 0: 
			    c = c + 1;
			    if c > 0:
				for filename in os.listdir(root):
				    #print "\n***\t"+filename
				    jsdata = open(os.path.join(root,filename),"r")
				    jso = json.load(jsdata)
				    
				    
				    #do language detection
				    if jso["text"] == "" or len(jso["text"]) < 2:
					print "\tERROR: No text in "+filename  
					try:
					    jso["language"] = detect(jso["title"])
					except:# LangDetectException:
					    jso["language"] = "en"
				    else:
					try:
					    jso["language"] = detect(jso["text"]) 
					except:# LangDetectException:
					    try:
						jso["language"] = detect(jso["title"])
					    except:
						jso["language"] = "en"
					
				    #print jso
				    
				    if jso["language"] == "es":
					db.texnews.spanish.insert(jso)
					es_cnt = es_cnt + 1
				    else:                                
					db.texnews.english.insert(jso)
					en_cnt = en_cnt + 1
				    cur = cur + 1
	    print str(cur)


#before adding just with houston we have
#> db.texnews.english.count()  731273
#> db.texnews.spanish.count()   15514

def add_dallas(db,searchfor):
	#DALLAS NEWS  (just Garnet Coleman search from mediacloud)  :: NOW DO FROM SEARCH FORMS 
	dallas_path = "/Users/dolano/htdocs/dama-larca/data/garnet-dallas/garnet_json/" + searchfor
	c = 0
	es_cnt = 0
	en_cnt = 0
	for root, subFolders, files in os.walk(dallas_path):    
	    if subFolders == []:          
		if len(os.listdir(root)) > 0: 
			c = c + 1;
			if c > 0:
			    for filename in os.listdir(root):
				#print "\n***\t"+filename
				jsdata = open(os.path.join(root,filename),"r")
				jso = json.load(jsdata)


				#do language detection
				if jso["text"] == "" or len(jso["text"]) < 2:
				    print "\tERROR: No text in "+filename  
				    try:
					jso["language"] = detect(jso["title"])
				    except:# LangDetectException:
					jso["language"] = "en"
				else:
				    try:
					jso["language"] = detect(jso["text"]) 
				    except:# LangDetectException:
					try:
					    jso["language"] = detect(jso["title"])
					except:
					    jso["language"] = "en"

				#print jso

				if jso["language"] == "es":
				    db.texnews.spanish.insert(jso)
				    es_cnt = es_cnt + 1
				else:                                
				    db.texnews.english.insert(jso)
				    en_cnt = en_cnt + 1                        


	#now we have 
	#> db.texnews.english.count() 731325


def add_texas_tribune(db,searchfor):
	#NOW ADD TEXAS TRIBUNE , (just Garnet Coleman search http://www.texastribune.org/search/?q=Garnet+Coleman)
	txtribune_path = "/Users/dolano/htdocs/dama-larca/data/txtribune/" + searchfor
	c = 0
	es_cnt = 0
	en_cnt = 0
	for root, subFolders, files in os.walk(txtribune_path):    
	    if subFolders == []:          
		if len(os.listdir(root)) > 0: 
			c = c + 1;
			if c > 0:
			    for filename in os.listdir(root):
				
				if ".json" in filename and "txtb" in filename:
				    print "\n***\t"+filename
				    jsdata = open(os.path.join(root,filename),"r")
				    jso = json.load(jsdata)


				    #do language detection
				    if jso["text"] == "" or len(jso["text"]) < 2:
					print "\tERROR: No text in "+filename  
					try:
					    jso["language"] = detect(jso["title"])
					except:# LangDetectException:
					    jso["language"] = "en"
				    else:
					try:
					    jso["language"] = detect(jso["text"]) 
					except:# LangDetectException:
					    try:
						jso["language"] = detect(jso["title"])
					    except:
						jso["language"] = "en"

				    #print jso

				    if jso["language"] == "es":
					db.texnews.spanish.insert(jso)
					es_cnt = es_cnt + 1
				    else:                                
					db.texnews.english.insert(jso)
					en_cnt = en_cnt + 1      

	print "found ",es_cnt," in spanish"   #0
	print "found ",en_cnt," in english"   #245



#NOW after add 245
#> db.texnews.english.count() 731570
#NOW ADD AUSTIN AMERICAN STATESMAN for GARNET COLEMAN ( http://www.statesman.com/search/?q=Garnet+Coleman)
def add_austinamericanstatesmen(db,searchfor):
	aastatesman_path = "/Users/dolano/htdocs/dama-larca/data/austinamericanstatesman/"+searchfor
	c = 0
	es_cnt = 0
	en_cnt = 0
	for root, subFolders, files in os.walk(aastatesman_path):    
	    if subFolders == []:          
		if len(os.listdir(root)) > 0: 
			c = c + 1;
			if c > 0:
			    for filename in os.listdir(root):
				
				if ".json" in filename and "aas" in filename:
				    print "\n***\t"+filename
				    jsdata = open(os.path.join(root,filename),"r")
				    jso = json.load(jsdata)


				    #do language detection
				    if jso["text"] == "" or len(jso["text"]) < 2:
					print "\tERROR: No text in "+filename  
					try:
					    jso["language"] = detect(jso["title"])
					except:# LangDetectException:
					    jso["language"] = "en"
				    else:
					try:
					    jso["language"] = detect(jso["text"]) 
					except:# LangDetectException:
					    try:
						jso["language"] = detect(jso["title"])
					    except:
						jso["language"] = "en"

				    #print jso

				    if jso["language"] == "es":
					db.texnews.spanish.insert(jso)
					es_cnt = es_cnt + 1
				    else:                                
					db.texnews.english.insert(jso)
					en_cnt = en_cnt + 1      

	print "found ",es_cnt," in spanish"   #0
	print "found ",en_cnt," in english"   #108



#get rid of duplicates ..
def remove_duplicates(db):
	#NOTE: you need to do this for texnews.english and texnews.spanish 
	res2 = db.texnews.english.aggregate([{ "$group": { "_id": { "article-num": "$article-num" }, 
					       "count": { "$sum": 1 }, "docs": { "$push": "$_id" }}},
					    { "$match": { "count": { "$gt" : 1 }}}],allowDiskUse=True)
	print len(res2["result"])
	for resa in res2['result']:
	    print resa["_id"]["article-num"] + ": "+ str(resa["count"])
	    c = 0
	    print resa
	    for d in resa["docs"]:
		if c > 0: 
		    print "\t mark as duplicate:"+str(d)
		    if c == 1:
			print "\t\t !!! remove from mongod"
			db.texnews.english.remove({'_id': d})
		c = c + 1

	res3 = db.texnews.spanish.aggregate([{ "$group": { "_id": { "article-num": "$article-num" }, 
					       "count": { "$sum": 1 }, "docs": { "$push": "$_id" }}},
					    { "$match": { "count": { "$gt" : 1 }}}],allowDiskUse=True)
	print len(res3["result"])
	for resa in res3['result']:
	    print resa["_id"]["article-num"] + ": "+ str(resa["count"])
	    c = 0
	    print resa
	    for d in resa["docs"]:
		if c > 0: 
		    print "\t mark as duplicate:"+str(d)
		    if c == 1:
			print "\t\t !!! remove from mongod"
			db.texnews.spanish.remove({'_id': d})
		c = c + 1


def mongo_to_elastic(es,db):
	i = 0
	#for c in db.texnews.english.find({"news-source": {"$ne": "Houston Chronicle"}}):
	for c in db.texnews.english.find():
	    i+=1
	    c.pop(u'_id')
	    c["body"] = c["text"]
	    c.pop(u'text')
	    try:
		if i == 1:
		    print c
		es.index(index="texnews_english", doc_type='news_article', id=i, body=c)
	    except:
		print("error with "+str(i)+"\n")
		

	i = 0
	for c in db.texnews.spanish.find():
	    i = i + 1
	    c.pop(u'_id')
	    
	    c["body"] = c["text"]
	    c.pop(u'text')
	    es.index(index="texnews_spanish", doc_type='news_article', id=i, body=c)



#BEFORE RUNNING THIS:  delete elastic index by hand
conn = MongoClient() 
db = conn.newsdb 
es = Elasticsearch()

searchfor = sys.argv[1]
add_houstonchronicle(db,searchfor)
add_dallas(db,searchfor)
add_texas_tribune(db,searchfor)
add_austinamericanstatesmen(db,searchfor)

remove_duplicates(db)

mongo_to_elastic(es,db)
