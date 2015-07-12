from langdetect import detect, detect_langs
import sys, os
import json
import datetime
from pymongo import MongoClient
from elasticsearch import Elasticsearch
import time
#use newsdb

#from get_articles_for_person_then_find_and_save_relations import *

def add_source(db,searchfor,path):
	search_path = path #+"/" + searchfor
	c = 0
	es_cnt = 0
	en_cnt = 0
	for root, subFolders, files in os.walk(search_path):    
	    if subFolders == []:          
		if len(os.listdir(root)) > 0: 
			c = c + 1;
			if c > 0:
			    for filename in os.listdir(root):
				if "links-" not in filename and "error" not in filename:
					jsdata = open(os.path.join(root,filename),"r")
					jso = json.load(jsdata)

					#fix beto
					if "Beto" in search_path:
						jso["text"] = jso["text"].replace("O\u2019Rourke","Rourke").replace("O'Rourke","Rourke")
					
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
					jso["entity"] = searchfor.replace("_"," ")

					if jso["language"] == "es":
					    db.texnews.spanish.insert(jso)
					    es_cnt = es_cnt + 1
					else:                                
					    db.texnews.english.insert(jso)
					    en_cnt = en_cnt + 1                        


def remove_if_exists_in_mongo(db,searchfor):
	print "---REMOVE FROM MONGO 'entity':'"+searchfor+"' if it exists---"
	#remove from mongodb
	db.texnews.english.remove({"entity":searchfor})
	db.texnews.spanish.remove({"entity":searchfor})
	

def call_ner(searchfor):
	#searchfor = sys.argv[1]
	#make_large_network = sys.argv[2] #include_large
	debug = False 
	print "Generate Small and Medium json files for "+searchfor
	#r = start_process(searchfor,"","include_large",debug)   #context unused for now	#no debug by default... you should only need this if you run into problems
	command = "python get_articles_for_person_then_find_and_save_relations.py '"+searchfor+"' include_large > debug_and_backup_files/"+searchfor.replace(" ","_")+"-getarticles-"+time.strftime("%m-%d_%I-%M-%S") + ".debug"   #make foreground call ( cause massive parallelization can hose my compu )
	print "UNIX CALL: "+command
	os.system(command)


def start(searchfor,only_add=None):
	print "---IN ADD JSON FILES TO DB---"
	conn = MongoClient() 
	db = conn.newsdb 
	
	remove_if_exists_in_mongo(db,searchfor)  #keys in mongo have space and not _ which folders do have

	searchfor = searchfor.replace(" ","_")

	#TODO PUT THESE SOURCES INTO A CONFIG JSON FILE
	sources = {"austinamericanstatesman","dallasnewssearch","houstonchronsearch","txobserver","txtribune","nytimes"}	
	for s in sources:
		print "ADD "+s+" json article data for "+searchfor
		add_source(db,searchfor,"data/"+s+"/"+searchfor)

	if only_add == None:
		call_ner(searchfor.replace("_"," "))	
	else:
		print "Just add, so you are done"

	
if __name__ == '__main__':
	#python add_json_files_for.py "Kyle Janek"
	searchfor = sys.argv[1]
	if len(sys.argv) > 2:
		#if a second arg is included don't do NER stuff, just do add to DB
		only_add = sys.argv[2]   #use this if you just want to add to DB and not continue (for debug purposes, normal use is not to pass a second param)
	else:
		only_add = None
	start(searchfor,only_add)
