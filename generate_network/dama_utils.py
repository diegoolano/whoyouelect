from __future__ import unicode_literals
from ftfy import fix_text
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters

import json
import sys
from functools import wraps
import errno
import os
import signal

#for federal_photo getter
#from bs4 import BeautifulSoup
#import requests
import traceback

class TimeoutError(Exception):
    pass

def timeout(seconds=10, error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator


def printflush(x,nl=True):    
    try:
        if nl == True:
            sys.stdout.write("\n"+x)
        else:
            sys.stdout.write(x)
    except:
	try:
		sys.stdout.write(str(x))
	except:
		try:
			print(x)
		except:
			print("still couldn't print prior!")
			traceback.print_exc(file=sys.stdout)
        
    sys.stdout.flush()

def get_federal_photo(url):
	#might be unnecessary actually since they all follow same structure
	print "Getting photo for url: "+url
	'''
	ret = ""
	try:
		page = requests.get(url) #,verify=False,timeout=20)
		soup = BeautifulSoup(page.content)
		photodiv = soup.find('div',{'class':'photo'})
		if photodiv != None and photodiv != '':
			img = startsoup.find('img')
			ret = "www.govtrack.us" + img.attrs['src']
			print "Found image: "+ret
	except:
		print "Error getting url"
		traceback.print_exc(file=sys.stdout)
		
	return ret
	'''

def remove_inactive_active_people(db):
	#there are some people who are both "statewide-active"/"statewide-inactive" ( Allen Fletcher )
	stateactive = db.texnews.entities.find({"level":"statewide-active"})
	print "PRIOR TO UPDATE THERE ARE: "+ str(db.texnews.entities.count())+" entities"
	for sa in stateactive:
		name = sa["full_name"]
		if name == "Allen Fletcher":
			print "Print checking Allen Fletcher"
		stateinactive = db.texnews.entities.find({"level":"statewide-inactive"})
		for si in stateinactive:
			if name == "Allen Fletcher":
				print "----"+si["full_name"]
			if name == si["full_name"]:
				print "Found match between: "+name+" (state active)  and "+si["full_name"]+" (inactive) so delete inactive id"
				print si
				db.texnews.entities.remove({"_id":si["_id"]})

	print "AFTER SA UPDATE THERE ARE: "+ str(db.texnews.entities.count())+" entities"
	federalactive = db.texnews.entities.find({"level":"federal-active"})
	for fa in federalactive:
		name = fa["full_name"]
		stateinactive = db.texnews.entities.find({"level":"statewide-inactive"})
		for si in stateinactive:
			if name == si["full_name"]:
				print "Found match between: "+name+" (federal active)  and "+si["full_name"]+" (inactive) so delete inactive id"
				print si
				db.texnews.entities.remove({"_id":si["_id"]})

	print "AFTER FA UPDATE THERE ARE: "+ str(db.texnews.entities.count())+" entities"
	stateelected = db.texnews.entities.find({"level":"statewide-active-elected"})
	for fa in federalactive:
		name = fa["full_name"]
		stateinactive = db.texnews.entities.find({"level":"statewide-inactive"})
		for si in stateinactive:
			if name == si["full_name"]:
				print "Found match between: "+name+" (statewide active elected)  and "+si["full_name"]+" (inactive) so delete inactive id"
				print si
				db.texnews.entities.remove({"_id":si["_id"]})
	
			
def save_legislators_to_from_mongo(db):
	#http://openstates.org/api/v1/legislators/?state=tx&apikey=744e7bf0a08748e69f06d690d8aa197c
	txf = open("/Users/dolano/htdocs/dama-larca/d3/whoyouelect/whoyouelect.com/texas/js/tx-legislators-asofMay10.json")
	data = json.load(txf)

	#http://openstates.org/api/v1/legislators/?state=tx&apikey=744e7bf0a08748e69f06d690d8aa197c&active=false
	txf_inactive = open("/Users/dolano/htdocs/dama-larca/d3/whoyouelect/whoyouelect.com/texas/js/tx-legislators-asofMay10inactive.json")
	data_inactive = json.load(txf_inactive)

	print "PRIOR TO UPDATE THERE WERE: "+ str(db.texnews.entities.count())+" entities"
	db.texnews.entities.remove()

	for pol in data:
	    pol["entity_type"] = "politician"
	    pol["level"] = "statewide-active"
            if 'chamber' in pol:
		if pol['chamber'] == 'lower':
			pol['position'] = 'Representative'
		else:
		   pol['position'] = 'Senator'
	    else:
		pol['position'] = 'Senator'
	    if 'party' not in pol:
		pol['party'] = "Republican"

	    #openstates info here is incorrect.  Dan Patrick currently is LTGov
	    if pol['full_name'] != 'Dan Patrick':
		db.texnews.entities.insert(pol)


	for pol in data_inactive:
	    pol["entity_type"] = "politician"
	    pol["level"] = "statewide-inactive"
	    db.texnews.entities.insert(pol)
    
	print "AFTER UPDATE WITH STATE LEVEL THERE ARE: "+ str(db.texnews.entities.count())+" entities"

	#now add federal level folks
	#https://www.govtrack.us/api/v2/role?current=true&state=TX
	txfed = open("/Users/dolano/htdocs/dama-larca/d3/whoyouelect/whoyouelect.com/texas/js/federallvl-texas.json")
	datafed = json.load(txfed)
	
	#go through and add full_name by combining firstname and lastname
	#and then call person->link  and get image from it ( scrape it )
	for pol in datafed["objects"]:
	    pol["entity_type"] = "politician"
	    pol["full_name"] = pol["person"]["firstname"] + " "+ pol["person"]["lastname"]
	    pol["photo_url"] = "http://www.govtrack.us/data/photos/" + pol["person"]["link"].split("/")[-1] + "-200px.jpeg" 
	    pol["level"] = "federal-active"
	    pol['position'] = pol['title_long']
	    
	    #print "ADDED: "+pol["full_name"] + ", "+pol["party"] + " - " + pol["title_long"] + ", "+pol["photo_url"]
	    db.texnews.entities.insert(pol)
		 
	print "AFTER UPDATE WITH FED LEVEL THERE ARE: "+ str(db.texnews.entities.count())+" entities"

	#http://www.sos.state.tx.us/elections/voter/elected.shtml || see htmltable_to_json.js
	txelc = open("/Users/dolano/htdocs/dama-larca/d3/whoyouelect/whoyouelect.com/texas/js/tx-electedofficials.json")
	dataelc = json.load(txelc)
	
	for pol in dataelc:
	    pol["entity_type"] = "politician"
	    pol["full_name"] = pol["officeholder"].replace("Honorable ","")
	    pol["position"] = pol["office"].split(">")[1].split("<")[0]
	    pol["level"] = "statewide-active-elected"
	    #TODO: this probably will have to be by hand
	    # pol["photo_url"] = "http://www.govtrack.us/data/photos/" + pol["person"]["link"].split("/")[-1] + "-200px.jpeg" 
	    pol["photo_url"] = ""
	    if pol['party'] == 'R':
		pol['party'] = "Republican"
	    else:
		pol['party'] = "Democrat"
	    pol["link"] = pol["office"]
	    
	    print "ADDED: "+pol["full_name"] + "| "+pol["party"] + " - " + pol["position"] + " | "+pol["photo_url"]
	    db.texnews.entities.insert(pol)
		 
	print "AFTER UPDATE WITH TEXAS LEVEL ELECTED THERE ARE: "+ str(db.texnews.entities.count())+" entities"
	res = get_active_entities(db)
	print "NUMBER OF ACTIVE: "+ str(res.count())
	res_sorted = res.sort("full_name",1)
	rescsv = ""
	for r in res_sorted:
		print r["full_name"] + " | " + r['level'] + ' | ' + r['position'] + ' | ' + r['party'] 
		rescsv = rescsv +'"'+r["full_name"].replace('"','') + '",' + r['level'] + ',' + r['position'].replac(",","") + ',' + r['party'].replace(",","") + "\n" 

	#create csv file of the above
	try:
		f = open('active-entities-list.csv','w')
		f.write(rescsv) # python will convert \n to os.linesep
		f.close() # you can omit in most cases as the destructor will call if			
	except:
		print "ERROR SAVING SLOWSTATS CSV FILE"
		traceback.print_exc(file=sys.stdout)
	

def get_active_entities(db):
	return db.texnews.entities.find({"level": { '$in': ["statewide-active","federal-active","statewide-active-elected"]}})

def get_entities(query,db):
    #for now this just gets legislators
    return db.texnews.entities.find(query)

def get_article_from_mongo_by_id(id,db):
    return db.texnews.english.find_one({'_id':id})
    
def generate_pol_query(pobj):    
    name = pobj["full_name"]
    party = pobj["party"]
    pos = "Senator"
    if pobj["chamber"] == "lower":
        pos = "Rep"
    #TODO maybe add district name (name of town or district)
    return [party + " " +pos, name] 

def run_pol_elastic_query(q,db):

    '''
    query = q[0]
    name = q[1]
    origq = {"query":{"bool":{"disable_coord": True,"must": [{'match_phrase': {'body': {'query':name, 'analyzer':'analyzer_keywords' }}}],
                          "should":[{'match':{'body':{'query':query}}}]}}}
    results = es.search(index='texnews_english',size=10000, body=origq)
    if len(results['hits']['hits']) == 0:        
        printflush("none found so new query: " + name)
        newq = {"query":{"bool":{"disable_coord": True,"must": [{'match_phrase':{'body':{'query':name,'analyzer':'analyzer_keywords'}}}]}}}
        results = es.search(index='texnews_english',size=10000, body=newq)
    '''
    query = q[0]
    name = q[1]
    results = db.texnews.english.find({"entity":name},timeout=False)
    results_sp = db.texnews.spanish.find({"entity":name},timeout=False)
    if results_sp.count() == 0:
    	return results     #only found english results
    elif results.count() == 0:
	return results_sp  #only found spanish results
    else:
	#MERGE THE TWO INTO ONE
	return [results,results_sp]


def get_article_sentences(article):
	#TODO: put this in db or config file
	subs = {'Sen.':'Senator','Lt. Gov.':'Lieutenant Governor','Rep.':'Representative', 
	    'Reps.':'Representatives,', 'Gov.':'Governor'}

	#if '_source' in article:
	if 'body' in article:
		text = fix_text(article['body']).replace('?"', '? "').replace('!"', '! "').replace('."', '. "')
		for a in subs:
			text = text.replace(a,subs[a])
			sentences = sentence_splitter.tokenize(text)
		return sentences
	return []

def entity_in_article(article,q,debug=False):
    #TODO HANDLE FALSE POSITIVE ON NAME!  for instance searching for "Scott Sanford" gets Jeffrey Scott Sanford
    #if prior character is punctuation or not a name ()
    #print article
    #print q
    query = q[0]
    name = q[1] 
    if '_source' in article:
        r = article['_source']        
        if 'body' in r:
            query_in_art = r['body'].find(query)
            if query_in_art > -1:
                if debug:
                    printflush("***Found query: "+query+" in article!")
                return True
            else:
                name_in_art = r['body'].find(name)
                if name_in_art > -1:
                    if debug:
                        printflush("***Found name: "+name+" in article!")
                    #TODO instead of return true immediately, look for Rep or Republican or anything from orginal query
                    #within some distance of the match to verify, we have something!
                    #or use nltk to check if prior or following word is a name
                    return True
    return False


def search_article_for_entity(sentences,q):
    #TODO refactor this to make it more generalizable if need be
    query = q[0]
    name = q[1]
    
    sentences_length = len(sentences)
    for s in sentences:
        loc = s.find(query)
        if loc > -1:
            printflush("*** Full found: " + r['date'] + ", " + r['section'] + " ," + r['title'] + " ," + r['article-num'])
            printflush("\t"+r['body'][loc-10:loc+len(query)])
        else:
            loc = r['body'].find(name,start)
            if loc > -1:
                    printflush("*** Name found at spot( "+str(loc)+" of "+str(len(r['body']))+" ): " + r['date'] + ", " + r['section'] + " ," + r['title'] + " ," + r['article-num'])
                    temp = r['body']            


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


from pymongo import MongoClient
from elasticsearch import Elasticsearch

#GLOBAL VARS
es = Elasticsearch()
conn = MongoClient()
db = conn.newsdb   #db is called "newsdb"

punkt_param = PunktParameters()
sentence_splitter = PunktSentenceTokenizer(punkt_param)
    
number_sentences_for_context = 3;
