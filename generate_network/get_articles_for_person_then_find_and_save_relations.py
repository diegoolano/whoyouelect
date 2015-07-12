from dama_globals import *
from dama_utils import *
from dama_ner import *
from entity_funcs import *
from handle_funcs import *
from verify_and_save_relations import *
import time
import traceback
	
from wiki_funcs import *
from generate_single_network import *
import sys

try:
	import cPickle as pickle
except:
	import pickle

import datetime
from dateutil.parser import *
import copy
import os
import gc

basep = "/Users/dolano/htdocs/dama-larca/d3/"    #BASE PATH 
save_configcomplete_file = basep + "generate_network/data/numbers/article-processing-results.json"


def handle_date(art):
	#http://stackoverflow.com/questions/16870663/how-do-i-validate-a-date-string-format-in-python
	#expected format: 2015-04-16
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
				printflush("ERROR couldn't find 'date' or 'time' in article:")
				printflush(art)
		else:
			date_text = art['date']
			dt = parse(date_text)	
			ntime = dt.strftime("%Y-%m-%d")
			art['date'] = ntime
			success = 1
			
	except:
		printflush("In HANDLE DATE WITH ART: "+art["url"]+" .. BAD DATE FORMAT IN JSON SO LOOK IN URL FOR A DATE OR JUST GIVE IT A DUMMY DATE")    #Abel Herrero 59,68,75,124,125
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
							printflush("NEWDATE: "+date_text)
							break
					break
			if success == 0:
				#still no luck so default to dummy date of 2000-01-01
				dt = parse("2000-01-01")
				ntime = dt.strftime("%Y-%m-%d")
				art['date'] = ntime 
				if 'time' in art: del art['time']
				printflush("NEWDATE: DEFAULT: 2000-01-01")
				success = 1
		except:
			printflush("STILL COULDNT HANDLE DATE SO SKIP ARTICLE")
			traceback.print_exc(file=sys.stdout)
				
			

	return [success,art]

def process_results(rcount,results,center_entity,q,debug,reprocess_stage,ri,make_large_network):
	article_entity_lens = {}
	global larger_relations
	global global_entities

	#if center_entity == "Beto Rourke":
	if center_entity == "J.D. Sheffield":
		#search by last name only
		printflush("CHANGING BETO's NAME")
		center_entity = "Sheffield"
		q[1] = "Sheffield"

	local_urls_seen = {}  #this is to remove duplicates
	
	printflush("\nIn process results with rcount: "+str(rcount))
	completed = 0
	a = 0  #index variable to keep track for debugging
	reprocess = []
	watchlist = [] #33, 42, 59,68,75,124,125]

	end_stats = {'totalinsts':0,'totalents':0,'totalrels':0,'totalsents':0,"ORGANIZATION":0, "BILL": 0, "MISC":0, "LOCATION":0,"PERSON":0,"politician":0,'completed':0, 'articles':rcount, 'processingtime':0}
	end_stats_res = {}
	slowresultscheck = "id,url,entities,sentences,ratio,processing_time,error,num_inst,is_results_or_list\n"
	slowresultschecklist = []
	for art in results:
		try:

			artstart = time.clock()

			if a == rcount:
				break
			else:
				a = a + 1

			if reprocess_stage == True:
				printflush("RRRR Reprocessed Iteration for a: "+str(a)+" and url: "+art["url"])

			if debug or a in watchlist: #or a in [1097,1225,1261]:
			    printflush("****"+str(a)+"*****************************************************************************************************")
			    printflush("\n"+str(a)+"Looking at-- id: "+str(art['_id'])+", source: "+art['news-source']+", "+art['url'])
			else:            
			    #printflush(str(a)+", ",False)
			    printflush("\n"+str(a)+"Looking at-- id: "+str(art['_id'])+", source: "+art['news-source']+", "+art['url'])
			    debug = False
	

			#kick out sports articles
			if "/sports/" in art["url"]:
				printflush("\nSKIP SPORTS ARTICLE!")
				continue	

			#look for dupes
			if art["url"] in local_urls_seen:
				printflush("\n ALREADY HANDLED THIS ARTICLE AT INDEX: "+str(local_urls_seen[art["url"]])+" SO SKIP IT")
				continue
			else:		
				local_urls_seen[art["url"]] = a
			

			#pre-check things are in order 
			success,art = handle_date(art)
		
			if success == 0:
				#something wrong happened here:  TODO start making more try/catch around the big functions to isolate errors STREAM ioctl timeout, etc
				printflush("\nSKIP ARTICLE (date issue for "+art['url']+" )")
				watchlist.append(a)
				continue

			if 'body' not in art and 'text' in art:
				art['body'] = art['text']
				del art['text']

			#beto specific
			art['body'] = art['body'].replace("O\u2019Rourke","Rourke")
			art['body'] = art['body'].replace("J.D. Sheffield","Sheffield")

			
			if debug:
			    printflush("ARTICLE TEXT: " + str(art))
			    
			sentences = get_article_sentences(art)  #dama_utils

			if debug:
				printflush(sentences)
			
			#named entity resolution software does better if center_entity is case specific correct
			for ind,sen in enumerate(sentences):
				if center_entity.upper() in sen:
					try:
						#print ("Found "+center_entity.upper()+" some make it normal size. "+sen)
						sentences[ind] = sentences[ind].replace(center_entity.upper(), center_entity)				
					except:	
						print ("Unable to make center_entity to upper for ind: "+str(ind))

			#add sentences to look up by url dic
			url_texts[art['url']] = sentences
			
			if debug:
			    printflush("\t--Found "+str(len(sentences))+" sentences")

			start_get_ner = time.clock()			
			#get list of entities found in article via MITIE
			#tokens, entities = get_named_entities(sentences)  #treating text as one piece
			entities, sentences = get_named_entities_per_sentence(sentences,debug) #instead try by sentence, dama_ner.py
			
			end_get_ner = time.clock()
			printflush("\nTIME INFORMATION get named entities took "+str(end_get_ner - start_get_ner)+" seconds")

			#before continuing make sure that full name of politician is a found entity (to avoid Jeffry Scott Sanford case)
			entities, found = verify_entity_found(entities,q[1],debug) 
			if found == False:
				#CHECK IF center_entity is "in" one of the entities

				printflush("\t\t"+q[1]+" not found in entities list for article so SKIP!!")
				#printflush(entities)
				#sys.exit()
				artend = time.clock()
				artelapsed = artend - artstart

				printflush("\n\t\tNUM INSTANCES FOUND: 0")
				printflush("\t\tNUM SENTENCES:   "+str(len(sentences)))
				#print entities
				'''
				[[{'text': 'Kyle Janek', 'score': '0.975', 'tag': 'PERSON'}, {'text': 'Texas', 'score': '0.704', 'tag': 'LOCATION'}], [{'text': 'GEO Care', 'score': '0.875', 'tag': 'ORGANIZATION'}, {'text': 'Frank Santos', 'score': '1.202', 'tag': 'PERSON'}, {'text': 'Janek', 'score': '0.565', 'tag': 'PERSON'}, {'text': 'GEO', 'score': '1.267', 'tag': 'ORGANIZATION'}], [{'text': 'Janek', 'score': '0.471', 'tag': 'PERSON'}, {'text': 'Health and Human Services Commission', 'score': '1.987', 'tag': 'ORGANIZATION'}]]
				'''
				#make dcount work along with thesedents work (it needs to be by TYPE and have sums for each)
				dcount = 0
				for d in entities:
					dcount = dcount + len(d)
				printflush("\t\tNUM DISENTITIES: "+str(dcount))
				thesedents = {"ORGANIZATION":0, "BILL": 0, "MISC":0, "LOCATION":0,"PERSON":0,"politician":0}
				for sen in entities:
					for en in sen:
						if en['tag'] not in thesedents:
							thesedents[en['tag']] = 1
						else:
							thesedents[en['tag']] = thesedents[en['tag']] + 1
				
				for d in thesedents:
					printflush("\t\t\t--"+d+": "+str(thesedents[d])+" entities")
					if d in end_stats:
						end_stats[d] = end_stats[d] + thesedents[d]
					else:
						end_stats[d] = thesedents[d]

				if len(sentences) == 0:
					printflush("ZERO SENTENCES IN ARTICLE "+art['url'])
					ratio = "0"
				else:
					ratio = str(round(float(dcount)/len(sentences),2))
				printflush("\t\tNUM RELATIONS:    0")
				printflush("\t\tAVG ENTITIES  PER SENTENCE: "+str(dcount)+"/"+str(len(sentences))+" = " + ratio)
				printflush("\t\tPROCESSING TIME (seconds) for ID("+str(a)+"): "+str(artelapsed))

				end_stats['totalinsts'] = end_stats['totalinsts'] + 0
				end_stats['totalsents'] = end_stats['totalsents'] + len(sentences)
				end_stats['totalents'] = end_stats['totalents'] + dcount
				end_stats['totalrels'] = end_stats['totalrels'] + 0
				end_stats['processingtime'] = end_stats['processingtime'] + artelapsed

				if art["news-source"] in end_stats:
					end_stats[art["news-source"]]["success"] = end_stats[art["news-source"]]["success"] + 1
				else:
					end_stats[art["news-source"]] = {"success": 1, "skipped":0 }

				thisstat =  {'url':art['url'],'processingtime':artelapsed,'insts':0,'ents':dcount,'rels':0,'sents':len(sentences), 'result':'skipped'}
				for d in thesedents:
					thisstat[d] = thesedents[d]
				end_stats_res[art['url']] = thisstat


				addstr = str(a)+","+art['url']+","+str(dcount)+","+str(len(sentences))+","+ratio+","+str(artelapsed)+",S,0,XXX\n"
				slowresultscheck = slowresultscheck + addstr
				slowresultschecklist.append(addstr)
				printflush("\t---set slowresults for "+art['url'])
				completed = completed + 1
				continue
				
			
			#disambiguate entity list ( i.e., Rick Perry = Gov Perry = Perry (depending on context) )         
			#as much as possible and create dictionary of who goes to who..
			#check to see who if any (and which aren't locations) exists in entity db
			#return json with keys for each entity, along with aliases for each and db info if any
			
			if debug: # or a == 366:# or a == 190:# or a == 50:# or a == 4:
			    printflush("\nYYYYYY Now Disambiguate")
			
			start_get_dis = time.clock()
			dis_entities = disambiguate_entities(entities,sentences,db,debug) #debug
			end_get_dis = time.clock()

			printflush("\nTIME INFORMATION disambiguate entities took "+str(end_get_dis - start_get_dis)+" seconds")
			if debug:
			    printflush("!!HERE IS THE LIST OF DISAMBIGUATED ENTITIES //first sentences  and then entities\n")
			    printflush(sentences)
			    for d in dis_entities:
				printflush(d)
				for de in dis_entities[d]:
				    printflush("\t"+de+" : "+ str(dis_entities[d][de]))
			

			if debug:
				printflush("Now Call Filter Entities")

			start_get_dis = time.clock()
			dis_entities = filter_entities(dis_entities,q[1],debug)
			end_get_dis = time.clock()
			printflush("\nTIME INFORMATION filter entities took "+str(end_get_dis - start_get_dis)+" seconds")


			#check to see if article is a list ( ie, if its ratio of totalentities per sentence is greater than ten, skip the article! )			
			dcount = 0
			for d in dis_entities:
				dcount = dcount + len(dis_entities[d])
			if len(sentences) == 0:
				ratio = 0
			else:
				ratio = round(float(dcount)/len(sentences),2)

			if ratio > 10 or ratio == 0 :
				printflush("\nThe ratio of number of distinct entities ("+str(dcount)+") to sentences ("+str(len(sentences))+") is "+str(ratio))
				if ratio == 0:
					printflush("This implies there are zero sentences so SKIP ARTICLE")
				else:
					printflush("This is too high so the article is most likely an list so SKIP THIS ARTICLE")
				artend = time.clock()
				artelapsed = artend - artstart

				printflush("\n\t\tNUM INSTANCES FOUND: 0 since we ")      #+str(len(relations[0]))
				printflush("\t\tNUM SENTENCES:   "+str(len(sentences)))
				printflush("\t\tNUM DISENTITIES: "+str(dcount))
				thesedents = {"ORGANIZATION":0, "BILL": 0, "MISC":0, "LOCATION":0,"PERSON":0,"politician":0}
				thesedents = {}
				for d in dis_entities:
					printflush("\t\t\t--"+d+": "+str(len(dis_entities[d]))+" entities")
					if d in end_stats:
						end_stats[d] = end_stats[d] + len(dis_entities)
					else:
						end_stats[d] = len(dis_entities)
						thesedents[d] = len(dis_entities)

				if len(sentences) == 0:
					printflush("ZERO SENTENCES IN ARTICLE "+art['url'])
					ratio = "0"
				else:
					ratio = str(round(float(dcount)/len(sentences),2))
				printflush("\t\tNUM RELATIONS:    0")
				printflush("\t\tAVG ENTITIES  PER SENTENCE: "+str(dcount)+"/"+str(len(sentences))+" = " + ratio)
				printflush("\t\tPROCESSING TIME (seconds) for ID("+str(a)+"): "+str(artelapsed))

				end_stats['totalinsts'] = end_stats['totalinsts'] + 0
				end_stats['totalsents'] = end_stats['totalsents'] + len(sentences)
				end_stats['totalents'] = end_stats['totalents'] + dcount
				end_stats['totalrels'] = end_stats['totalrels'] + 0
				end_stats['processingtime'] = end_stats['processingtime'] + artelapsed

				if art["news-source"] in end_stats:
					end_stats[art["news-source"]]["success"] = end_stats[art["news-source"]]["success"] + 1
				else:
					end_stats[art["news-source"]] = {"success": 1, "skipped":0 }

				thisstat =  {'url':art['url'],'processingtime':artelapsed,'insts':0,'ents':dcount,'rels':0,'sents':len(sentences), 'result':'skipped'}
				for d in thesedents:
					thisstat[d] = thesedents[d]
				end_stats_res[art['url']] = thisstat


				addstr = str(a)+","+art['url']+","+str(dcount)+","+str(len(sentences))+","+ratio+","+str(artelapsed)+",S,0,XXX\n"
				slowresultscheck = slowresultscheck + addstr
				slowresultschecklist.append(addstr)
				printflush("\t---set slowresults for "+art['url'])
				completed = completed + 1
				continue


			if debug:# or a==4:
			    debug = True
			    printflush("\nYYYYYY NOW NOW get relations!")
			
			start_get_rels = time.clock()
			relations = get_relations(q[1], entities,dis_entities,sentences,db,debug)    #entity_funcs.py      
			end_get_rels = time.clock()
			printflush("\nTIME INFORMATION get_relations took "+str(end_get_rels - start_get_rels)+" seconds")

			if debug:            
			    printflush("\n\nYYYYYY AFTER GET RELATIONS: Sentences:")
			    for szi,sz in enumerate(sentences):
				printflush(str(szi) +": " + sz)
			    printflush("\nRelations:")
			    printflush(relations)
			    printflush("\nEntities")
			    printflush(entities)
			    printflush("\nDis_entities")
			    printflush(dis_entities)
			    
			if debug:
			    debug = True
			    printflush("----------------------------------------------------------------------------------------")
			    printflush("XXXXXX VERIFY/CHECK IF ENTITIES EXIST IN DB and save.. for now just to local BIG list maybe?")

			#this only gives relations with direct relation to center_entity and not amongst them so we now need another function
			#which grabs all the links between the entities which have relations with the center_entity
					


			if a not in watchlist and reprocess_stage == False:
				add_extras = True   #BY DEFAULT ADD NON MAIN NODE LINKS AS WELL!
			else:
				add_extras = False

			if debug == debug:
				verify_start = time.clock()

			res = verify_and_save_relations(q,relations,dis_entities,sentences,art,add_extras,db,debug)   #verify and save.py   
				
			if debug == debug:
				verify_end = time.clock()
				printflush("\t\tTIME INFORMATION:  VERIFYING TOOK "+str((verify_end - verify_start))+" seconds")

			if make_large_network == "include_larger" or make_large_network == "include_large":
				if debug:
					printflush("CALL GET LARGER RELATIONS")

				#cur_verified_large  = verify_and_save_large_relations(q[1],prior_relations,dis_entities,sentences,art,add_extras,db,debug)
				cur_verified_large  = copy.deepcopy(res)
				larger_relations[art['url']] = cur_verified_large

				if debug:
					printflush("XXXX DONE WITH LARGER RELATIONS FOR ARTICLE")

			#TODO do verify and save relations for larger_relations!! here we need to have an independent "large" network we are saving too ( this will also include center_node )

			#add to article_entity centric
			article_entity_lens[a] = [len(res['relations']),art['_id'],art['url']]
			
			#debug = False
			if debug:
			    printflush("RESULTS FOR URL:")
			    
			    if len(relations[0]) > 1:        
				printflush("\nFOUND MULTIPLE DIRECT HITS at: "+ str(relations[0]))
										       
			    printflush("\nMADE THE FOLLOWING RELATIONS:")
			    for rel in res['relations']:  
				if 'sentence_num' in rel:
				    if rel['type'] == 'near':
					printflush("\t"+rel['term1'] + '('+str(rel['term1_id'])+') -- ' + rel['term2'] + '('+str(rel['term2_id'])+') of type: '+rel['type']+ " - "+rel['subtype']+"| "+str(rel['sentence_num']))
				    else:
					printflush("\t"+rel['term1'] + '('+str(rel['term1_id'])+') -- ' + rel['term2'] + '('+str(rel['term2_id'])+') of type: '+rel['type']+"| "+str(rel['sentence_num']))
				else:
				    printflush("\t"+rel['term1'] + '('+str(rel['term1_id'])+') -- ' + rel['term2'] + '('+str(rel['term2_id'])+') of type: '+rel['type'])
					
			    for ge in global_relations:  #global_index and global_entities are fine
				printflush(ge)
			

			#add relations stuff to json_output ( center node centric )
			if debug == debug: start_add_inter = time.clock()
			add_intermediate_json_relations(res,len(relations[0]),debug)    
			if debug == debug:
				end_add_inter = time.clock()
				printflush("\t\tTIME INFORMATION add_intermediate_json_relations took "+str(end_add_inter - start_add_inter)+" seconds")

			#now print out stats for article
			artend = time.clock()
			artelapsed = artend - artstart

			printflush("\n\t\tNUM INSTANCES FOUND: "+str(len(relations[0])))
			printflush("\t\tNUM SENTENCES:   "+str(len(sentences)))
			#dcount = 0
			#for d in dis_entities:
			#	dcount = dcount + len(dis_entities[d])
			printflush("\t\tNUM DISENTITIES: "+str(dcount))
			thesedents = {}
			for d in dis_entities:
				printflush("\t\t\t--"+d+": "+str(len(dis_entities[d]))+" entities")
				if d in end_stats:
					end_stats[d] = end_stats[d] + len(dis_entities)
				else:
					end_stats[d] = len(dis_entities)
					thesedents[d] = len(dis_entities)

			ratio = str(round(float(dcount)/len(sentences),2))
			printflush("\t\tNUM RELATIONS:   "+str(len(res['relations'])))
			printflush("\t\tAVG ENTITIES  PER SENTENCE: "+str(dcount)+"/"+str(len(sentences))+" = " + ratio)
			printflush("\t\tAVG RELATIONS PER SENTENCE: "+str(len(res['relations']))+"/"+str(len(sentences))+" = " + str(float(len(res['relations']))/len(sentences)))
			printflush("\t\tPROCESSING TIME (seconds) for ID("+str(a)+"): "+str(artelapsed))

			end_stats['totalinsts'] = end_stats['totalinsts'] + len(relations[0])
			end_stats['totalsents'] = end_stats['totalsents'] + len(sentences)
			end_stats['totalents'] = end_stats['totalents'] + dcount
			end_stats['totalrels'] = end_stats['totalrels'] + len(res['relations'])
			end_stats['processingtime'] = end_stats['processingtime'] + artelapsed
			
			if art["news-source"] in end_stats:
				end_stats[art["news-source"]]["success"] = end_stats[art["news-source"]]["success"] + 1
			else:
				end_stats[art["news-source"]] = {"success": 1, "skipped":0 }
			
			thisstat =  {'url':art['url'],'processingtime':artelapsed,'insts':len(relations[0]),'ents':dcount,'rels':len(res['relations']),'sents':len(sentences), 'result':'completed'}
			for d in thesedents:
				thisstat[d] = thesedents[d]
			end_stats_res[art['url']] = thisstat

			
			addstr = str(a)+","+art['url']+","+str(dcount)+","+str(len(sentences))+","+ratio+","+str(artelapsed)+",N,"+str(len(relations[0]))+",XXX\n"
			slowresultscheck = slowresultscheck + addstr
			slowresultschecklist.append(addstr)
			printflush("\t---set slowresults for "+art['url'])
			completed = completed + 1
			    
			#see if you can free up memory here for a speed up!
			gc.collect()
	
		#except Exception as e:
		except:


			printflush("ERROR at a "+str(a)+" WITH: ")
			#printflush("ERROR at a "+str(a)+" WITH "+ str(e))
			traceback.print_exc(file=sys.stdout)
			try:
				printflush("STATS COLLECTED ON ARTICLE AT INDEX "+str(a)+" BEFORE ERROR: ")
				printflush("===========================================")
				thisstat =  {'result':'skipped'} #'url':art['url'],'processingtime':artelapsed,'ents':dcount,'rels':len(res['relations']),'sents':len(sentences), 'result':'completed'}
				if 'art' in locals():
					printflush("\tARTICLE: "+art["url"])
					thisstat["url"] = art['url']
					thisstat["news-source"] = art["news-source"]
					
					#update universal stats
					if art["news-source"] in end_stats:
						end_stats[art["news-source"]]["skipped"] = end_stats[art["news-source"]]["skipped"] + 1
					else:
						end_stats[art["news-source"]] = {"success": 0, "skipped":1 }
			
				if 'sentences' in locals():
			    		printflush("\t--Found "+str(len(sentences))+" sentences")
					thisstat["sents"] = len(sentences)

				if 'entities' in locals():
				#	printflush("\t--Found "+str(len(entities))+" Entities BEFORE disambiguation") #this gives entities per sentence so get full count by sentence
					#printflush("\t--Found initial entities with len("+str(len(entities))+"): ")
					if len(entities) == 2:
						ecount = 0
						ees = entities[0]
						for eese in ees:
							ecount = ecount + len(eese)
						printflush("\t--TOTAL INITIAL ENTITIES_: "+str(ecount))
					else:
						ecount = 0
						ees = entities
						for eese in ees:
							ecount = ecount + len(eese)
						printflush("\t--TOTAL INITIAL ENTITIES:: "+str(ecount))
					
						
				if 'dis_entities' in locals():
					printflush("\t--Found "+str(len(dis_entities))+" Entities AFTER disambiguation")
					dcount = 0
					for d in dis_entities:
						#print d
						#print dis_entities[d]
						printflush("\t\t--"+d+": "+str(len(dis_entities[d]))+" entities")
						dcount = dcount + len(dis_entities[d])
						thisstat[d] = len(dis_entities[d])
					printflush("\t--TOTAL DISAMBIGUATED: "+str(dcount))
					thisstat["ents"] = dcount

				if 'relations' in locals():
					printflush("\t--NUM INSTANCES FOUND: "+str(len(relations[0])))
					thisstat['insts'] = len(relations[0])

				if 'sentences' in locals() and 'dis_entities' in locals():
					ratio = str(round(float(dcount)/len(sentences),2))
					printflush("\t--AVG ENTITIES PER SENTENCE: "+str(dcount)+"/"+str(len(sentences))+" = " + ratio)

				if 'artstart' in locals():
					artend = time.clock()
					artelapsed = artend - artstart
					printflush("\t--PROCESSING TIME (seconds) for ID("+str(a)+"): "+str(artelapsed))
					thisstat['processingtime'] = artelapsed

				if 'art' in locals() and 'sentences' in locals() and 'dis_entities' in locals() and 'relations' in locals() and 'artstart' in locals():
					addstr = str(a)+","+art['url']+","+str(dcount)+","+str(len(sentences))+","+ratio+","+str(artelapsed)+",Y,"+str(len(relations[0]))+",XXX\n"

					slowresultscheck = slowresultscheck + addstr
					printflush("\t---set slowresults for "+art['url'])
					slowresultschecklist.append(addstr)
				if 'art' in locals():
					end_stats_res[art['url']] = thisstat
			except:
				traceback.print_exc(file=sys.stdout)

			reprocess.append(art)

	printflush("\n=====Done with processing articles: ")
	if rcount == 0:
		printflush("=====No Articles=====")
	else:
		printflush("=====Succesffully included: "+str(completed)+" out of "+str(rcount)+" ("+str(float(completed)/rcount)+" %)")
		end_stats["completed"] = completed

		#save for later use... 
		try:
			with open(save_configcomplete_file, 'rb') as configcomplete:
				configjson = json.load(configcomplete)
				ri = str(ri)  #ri is to distinguish between english(0) and spanish(1) results
				if reprocess_stage == False:
					if center_entity in configjson:
						if ri in configjson[center_entity]:
							configjson[center_entity][ri]["firstpass"] = [end_stats,end_stats_res]
						else:
							configjson[center_entity][ri] = {"firstpass": [end_stats,end_stats_res]}
					else:
						configjson[center_entity] = {ri : {"firstpass": [end_stats, end_stats_res]}}
				else:
					configjson[center_entity][ri]["secondpass"] = [end_stats,end_stats_res]
					
				configcomplete.close()	
			
				with open(save_configcomplete_file, 'wb') as fp:
					json.dump(configjson, fp)
		except:
			printflush("ERROR SAVING STATS FILE")
			traceback.print_exc(file=sys.stdout)
			try:
				printflush("TRY JUST PRINTING OUT UPDATE configjson TO LOG:  configjson")
				ri = str(ri)  #ri is to distinguish between english(0) and spanish(1) results
				if reprocess_stage == False:
					if center_entity in configjson:
						if ri in configjson[center_entity]:
							configjson[center_entity][ri]["firstpass"] = [end_stats,end_stats_res]
						else:
							configjson[center_entity][ri] = {"firstpass": [end_stats,end_stats_res]}
					else:
						configjson[center_entity] = {ri : {"firstpass": [end_stats, end_stats_res]}}
				else:
					configjson[center_entity][ri]["secondpass"] = [end_stats,end_stats_res]

				print configjson
			except:
				printflush("ERROR just printing out stats failed!")
				traceback.print_exc(file=sys.stdout)
		
		#save numbers for slowclassifier check
		try:
			f = open('data/numbers/slowclassdata-'+center_entity.replace(" ","_")+"-"+str(ri)+".csv",'w')
			f.write(slowresultscheck) # python will convert \n to os.linesep
			f.close() # you can omit in most cases as the destructor will call if			

			#write csv based on slowresultschecklist
			f = open('data/numbers/slowclassdata-'+center_entity.replace(" ","_")+"-"+str(ri)+"-fromlist.csv",'w')
			f.write("".join(slowresultschecklist)) # python will convert \n to os.linesep
			f.close() # you can omit in most cases as the destructor will call if			
			
		except:
			printflush("ERROR SAVING SLOWSTATS CSV FILE")
			traceback.print_exc(file=sys.stdout)
			try:
				print slowresultscheck
			except:
				printflush("ERROR just printing csv file failed!")
				traceback.print_exc(file=sys.stdout)
			

	if reprocess_stage == False:
		printflush("WWWWW Reprocess Num of Articles ("+str(len(reprocess))+"): ")  #probably instead should just do try catch around verify and save ( if using add extras == True, and try again with False )
		printflush(watchlist)
		if len(reprocess) > 0:
			process_results(len(reprocess),reprocess,center_entity,q,debug,True,ri,make_large_network)


def generate_url_list():
    #make url list indexed by mongoid so that edges just need mongoid to show id
    url_list = {}
    for i,gr in enumerate(global_relations):
        mongoid = global_relations[gr]['mongoid']
        url_list[mongoid] = {'url':global_relations[gr]['url'], 'date': global_relations[gr]['date'],
                             'num_sentences':global_relations[gr]['num_sentences'], 
                             'entities':len(global_relations[gr]['entities']),
                             'relations':len(global_relations[gr]['relations'])}
    return url_list
    

def start_process(center_entity,context,make_large_network,debug=False):
	global global_entities
	if 'global_entities' not in globals():
		global_entities = []
		
	#get list of legislators (from mongodb)
	q = {'entity_type':'politician'}
	pols = get_entities(q,db)        #dama_utils  ,   print pols.count()

	#populate global entities locally, start with 183
	if len(global_entities) == 0:
		for p in pols:
			global_entities.append(p)
	    
	#make starting global index
	for i, j in enumerate(global_entities):
		global_index[j['full_name']] = i

	pols = get_entities(q,db)#have to re-get info
	start = time.clock()

	#currently don't use context at all
	q = [context,center_entity]

	printflush("***Currently on "+q[0]+" " + q[1]+"\n")

	iresults = run_pol_elastic_query(q,db)   #dama_utils.py  OLD WAY IS TO USE ELASTIC BUT NOW HIT MONGODB DIRECTLY SINCE WE HAVE "entity" key we can leverage

	if type(iresults) == list:
		#results return for both english and spanish dbs
		rcount = iresults[0].count() + iresults[1].count()
		setsfound = 2
	else:
		#results for only one of the two
		rcount = iresults.count()
		results = iresults
		setsfound = 1

	finalcount = rcount
	if rcount == 0:
		printflush("ERROR: No results found for "+center_entity+".  Check to see if search steps have been completed prior.  \n")
        	sys.exit()	
	else:
		printflush("found "+str(rcount) +" results.  Now inspecting article results: ")    
		
	if setsfound == 1:
		ri = 0
		process_results(rcount,results,center_entity,q,debug,False,ri,make_large_network)  #ri is only used for saving of stats purposes!
	else:
		#multiple language results found
		printflush("Found Results in multiple languages")
		for ri, results in enumerate(iresults):
			rrcount = results.count()
			process_results(rrcount,results,center_entity,q,debug,False,ri,make_large_network)
		
	end = time.clock()
	elapsed = end - start
	printflush("**************************************")
	printflush("TOTAL Elapsed Time: "+str(elapsed)+" seconds to process "+str(finalcount)+" articles")
	printflush("**************************************")

	
	pstart = time.clock()
	url_list = generate_url_list()
	
	basep = "/Users/dolano/htdocs/dama-larca/d3/"    #BASE PATH 
	datap = basep + "generate_network/"
	crr = center_entity.replace(" ","_")
	tarf = datap + "data/pickles/"+crr+".tar.gz"
	picklefile = datap + "data/pickles/"+crr+".pickle"

	printflush("Length of Larger Relations: "+str(len(larger_relations)))
	#save inbetween objects for later use ( to save time on debugging )
	with open(picklefile, 'wb') as f:
    		pickle.dump([global_index, entity_edges, global_entities, center_entity,json_output, text_snippets, global_relations, url_list, larger_relations ], f)
	
	#gzip file to save space ( seriously it goes from half a meg to 10MB !)
	printflush("Make tar file: "+tarf+" and save pickle to it")
	tar = tarfile.open(tarf, "w:gz")
	tar.add(picklefile)
	tar.close()

	if os.path.isfile(tarf):
		#rm pickle after you are sure backup exists
		printflush("Delete picklefile: "+picklefile)
		os.remove(picklefile)
	
	larger = False
	if make_large_network == "include_large" or make_large_network == "include_larger":
		#printflush("Include Large Network arg passed in")
		larger = True

	
	
	pend = time.clock()
	printflush("TIME INFO: to save pickle, tar it, and delete pickle it took: "+str(pend - pstart)+" seconds")
	

	#NOW TRY TO DO THIS AS AN OS COMMAND INSTEAD (to see if it speeds up)
	#NOW CONSTRUCT NETWORK OUTPUT FILE(S) FROM DATA

	if larger == True:
		also_larger = "include_larger" 
	else:	
		also_larger = "just_single"

	if debug:
		dd = "debug"
	else:
		dd = ""

	if finalcount < 10:  #its quicker to load straight from memory so only load from pickle if file is very small
		load_pickle = True
		#should i do this in the background or foreground ( if foreground allows get_articles to terminate and free memory/process after call and doesn't wait for response, keep it in foreground )
		command = "python generate_single_network.py '"+searchfor+"' "+also_larger+" "+dd+" > debug_and_backup_files/"+searchfor.replace(" ","_")+"-generate_single_net-"+time.strftime("%m-%d_%I-%M-%S") + ".debug &"
		printflush("UNIX CALL: "+command)
		os.system(command)
	else:
		load_pickle = False
		#it takes way too long loading from pickle usually so see how it does without loading from pickle
		generate_single_network(larger, center_entity, debug, load_pickle)   #first here is to specifiy if you want the larger network as well


if __name__ == '__main__':
	searchfor = sys.argv[1]
	if len(sys.argv) > 2:
		make_large_network = sys.argv[2] #include_large
	else:		
		make_large_network = "no"  #default to not making larger network

	if len(sys.argv) > 3:
		debug = True      #if any third arg present set debug 
	else:
		debug = False
	r = start_process(searchfor,"",make_large_network,debug)   #context unused for now	
