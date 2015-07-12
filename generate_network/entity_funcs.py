from dama_utils import *
from dama_globals import *
import sys
import copy
import traceback


def get_sentence_with_entity_id(id,entities,sentences,debug):
    if debug == True:
        printflush("looking for id: "+str(id))
    cur_sen = 0
    cur_ent = 0
    for sent in entities:
        for ind,e in enumerate(sent):
            if cur_ent == id:
                return [cur_sen, sentences[cur_sen]]
            else:
                cur_ent = cur_ent + 1
        cur_sen = cur_sen + 1
    return [-1,""]
    
def get_entities_for_sentence(sent_num,dis_entities,debug=False):
    if debug:
        printflush("In Get Entities for Sentence")
        printflush("Sent num: "+str(sent_num))
        printflush("DisEntities:")
        printflush(dis_entities)
        
    res = []
    for k in dis_entities:
        if debug:
            printflush("CATEGORY: " + k)  #"ORGANIZATION", "MISC", etc
        for ent in dis_entities[k]:
            ent_obj = dis_entities[k][ent]
            if debug:
                printflush("Ent: "+ ent)  #  "senate", "etc"
                printflush("Ent Obj")
                printflush(ent_obj)

            if sent_num in ent_obj['sentence']:
                indk = ent_obj['sentence'].index(sent_num)
                if debug:
                    printflush("Find "+str(sent_num)+" which is index: "+str(indk)+" in ent_obj above")
                res.append({"type":k,"name":ent,"ent_id":ent_obj['id'][indk]})
    
    if res != []:
        #sort by ent_id
        res = sorted(res)
             
    return res

def get_entities_for_surrounding_sentences(sent_num,dis_entities,upperbound,debug):
    #uses global var number_sentences_for_context
    
    #go backwards
    prior_sentences = []
    if sent_num > 0:
        start = sent_num - number_sentences_for_context 
        if start < 0:
            #get from 0 to sent
            start = 0
            
        while start < sent_num:
            prior_sentences.append(get_entities_for_sentence(start,dis_entities))
            start = start + 1

    #go forwards
    next_sentences = []
    if sent_num < upperbound:
        start = sent_num + 1 
        end = sent_num + number_sentences_for_context 
        if end > upperbound:
            if debug:
                printflush("End "+str(end)+" greater than upperbound "+ str(upperbound) + " so setting it to it")
            end = upperbound
        while start <= end:
            next_sentences.append(get_entities_for_sentence(start,dis_entities))
            start = start + 1        

    return [prior_sentences,next_sentences]

def get_entities_further_away_in_article(sent_num,dis_entities,upperbound,debug):
    #uses global var number_sentences_for_context
    if debug:
        printflush("In get entities further away in article with sentence: "+str(sent_num)+" , and upperbound: "+str(upperbound))
        
    #go backwards
    prior_farther_sentences = []
    if sent_num > 0:
        start = 0
        end = sent_num - number_sentences_for_context 
        if end >= 0:            
            while start < end:    #i think this needs to be strictly less than
                prior_farther_sentences.append(get_entities_for_sentence(start,dis_entities))
                start = start + 1

    if debug:
        printflush("prior: " + str(prior_farther_sentences))
        
    #go forwards
    next_farther_sentences = []
    if sent_num < upperbound:
        start = sent_num + number_sentences_for_context + 1 
        end = upperbound 
        if start < upperbound:          
            while start <= end:   #is this strict or equal/less
                next_farther_sentences.append(get_entities_for_sentence(start,dis_entities))
                start = start + 1        

    return [prior_farther_sentences,next_farther_sentences]


@timeout(50)
def get_larger_relations(starting_politician,entities,dis_entities,entrelations,sentences, db,debug):
	if debug:
		printflush("IN GET LARGER RELATIONS")

	global global_relations
	global global_entities
	
	larger_relations = {starting_politician: entrelations}

	#if debug:
		#printflush(global_entities)   at this point, global_entities only includes initial politicians from JSON

	#go through dis_entities ( excluding location ) and 
	#IMPORTANT I'm NOT INCLUDING LOCATIONS
	'''
	DisEntities:
	{'ORGANIZATION': {'Immigration and Customs Enforcement': {'entity_type': 'ORGANIZATION', 'id': [3], 'full_name': 'Immigration and Customs Enforcement', 'sentence': [2]}, 'University of Texas Immigration Law Clinic': {'entity_type': 'ORGANIZATION', 'id': [26], 'full_name': 'University of Texas Immigration Law Clinic', 'sentence': [15]}, 'ACLU': {'entity_type': 'ORGANIZATION', 'id': [25], 'full_name': 'ACLU', 'sentence': [15]}, 'ICE': {'entity_type': 'ORGANIZATION', 'id': [9, 10, 20], 'full_name': 'ICE', 'sentence': [4, 5, 12]}}, 
	 'BILL': {}, 
	 'MISC': {'Grassroots Leadership': {'entity_type': 'MISC', 'id': [31], 'full_name': 'Grassroots Leadership', 'sentence': [17]}}, 
	 'LOCATION': {'Dilley': {'entity_type': 'LOCATION', 'id': [4, 33], 'full_name': 'Dilley', 'sentence': [2, 18]}, 'Karnes City': {'entity_type': 'LOCATION', 'id': [16], 'full_name': 'Karnes City', 'sentence': [10]}, 'Honduras': {'entity_type': 'LOCATION', 'id': [13], 'full_name': 'Honduras', 'sentence': [7]}, 'El Salvador': {'entity_type': 'LOCATION', 'id': [14], 'full_name': 'El Salvador', 'sentence': [7]}, 'U.S.': {'entity_type': 'LOCATION', 'id': [2, 15], 'full_name': 'U.S.', 'sentence': [0, 9]}, 'Pennsylvania': {'entity_type': 'LOCATION', 'id': [18, 27], 'full_name': 'Pennsylvania', 'sentence': [11, 16]}, 'Guatemala': {'entity_type': 'LOCATION', 'id': [12], 'full_name': 'Guatemala', 'sentence': [7]}, 'South Texas': {'entity_type': 'LOCATION', 'id': [1, 11], 'full_name': 'South Texas', 'sentence': [0, 5]}, 'New Mexico': {'entity_type': 'LOCATION', 'id': [19], 'full_name': 'New Mexico', 'sentence': [11]}, 'AUSTIN': {'entity_type': 'LOCATION', 'id': [0, 24], 'full_name': 'AUSTIN', 'sentence': [0, 14]}, 'San Antonio': {'entity_type': 'LOCATION', 'id': [5, 17], 'full_name': 'San Antonio', 'sentence': [2, 10]}, 'Texas': {'entity_type': 'LOCATION', 'id': [22], 'full_name': 'Texas', 'sentence': [14]}, 'Laredo': {'entity_type': 'LOCATION', 'id': [34], 'full_name': 'Laredo', 'sentence': [18]}}, 
	 'PERSON': {'Adelina Pruneda': {'entity_type': 'PERSON', 'id': [6, 8, 21], 'full_name': 'Adelina Pruneda', 'sentence': [2, 4, 12]}, 'T. Don Hutto': {'entity_type': 'PERSON', 'id': [23, 28, 29], 'full_name': 'T. Don Hutto', 'sentence': [14, 16, 17]}, 'Bob Libal': {'entity_type': 'PERSON', 'id': [30, 32, 35], 'full_name': 'Bob Libal', 'sentence': [17, 18, 19]}}}
	'''

	local_entities_seen = [starting_politician]
	dis_entities_copy = copy.deepcopy(dis_entities)

	#NO LONGER REMOVE LOCATION FROM dis_entities first	
	#del dis_entities_copy['LOCATION']

	for t, tels in dis_entities_copy.iteritems():
		if t != "LOCATION2":   #THIS HAS BEEN CHANGED SO LOCATIONS ARE OKAY NOW
			for tentname,tentdata in tels.iteritems():
				if tentname in local_entities_seen:
					if debug:
						printflush("\nARRIVED AT: "+tentname+" who we've already seen so skip")
					continue
				if debug:
					printflush("\nZZZZ ADDING RELATIONS FOR "+tentname+" ("+t+")\n")
				tentrelations = get_relations(tentname,entities,dis_entities_copy,sentences,db,debug)
				if debug:
					printflush("\nZZZZ AFTER GET RELATIONS CALLED FOR "+tentname+"\n")
					printflush("For Sentences: ") 
					printflush(sentences)
            				printflush("\n RELATIONS IN ARRAY with structure: [[sentences_where_entity_appeasr][same_sent, prior_sents, next_sents, prior_far, next_far]]")
					printflush("\nTHE FOLLOWING RELATIONS WERE FOUND FOR "+tentname)
					printflush(tentrelations)
				
				#NOW REMOVE ANY RELATIONS WHICH ALREADY EXIST IN PRIOR local_entities_seen or that are LOCATIONS (those these shouldn't exist)

				tentsents, tentrs = tentrelations
				for l in local_entities_seen:
					for reltype in tentrs:
						for r in reversed(reltype):
							if debug:
								printflush("r\n")
								printflush(type(r))
								printflush(r)
							if type(r) == dict:
								if debug:
									printflush("DICT FOUND")
								if r['name'] == l or r['type'] == 'LOCATION2':
									if debug:
										printflush("FOUND "+r['name']+" ("+r['type']+") in reltype SO DELETE IT")
									reltype.remove(r)
							else:
								if debug:
									printflush("NOT DICT")
									printflush("rr\n")
									printflush(r)

								for e in reversed(r):
									if debug:
										printflush("e\n")
										printflush(type(e))
										printflush(e)
									if type(e) == dict:
										if e['name'] == l or e['type'] == 'LOCATION2':
											if debug:
												printflush("FOUND "+e['name']+"("+e['type']+") in r SO DELETE IT")
											r.remove(e)	
									else:
										for b in reversed(e):
											if debug:
												printflush("b\n")
												printflush(type(b))
												printflush(b)
											if type(b) == dict:
												if b['name'] == l or b['type'] == 'LOCATION2':
													if debug:
														printflush("FOUND "+b['name']+" ("+b['type']+") in e SO DELETE IT")
													e.remove(b)	
											else:
												if debug:
													printflush("HUGE ERROR need to take of this")
				if debug:
					printflush("POST EXPUNGE for "+tentname+" [you shouldn't see any of the following entities]")
					printflush(local_entities_seen)
					printflush(tentrs)
					printflush(tentrs == tentrelations[1])
			
				local_entities_seen.append(tentname)

				larger_relations[tentname] = tentrelations
				
	if debug:
		printflush("YYYYY OVERALL LARGE NETWORK") 
		printflush(larger_relations)

	return larger_relations


@timeout(50)
def get_relations(starting_politician, entities,dis_entities,sentences,db,debug):
    #TODO maybe add rules for how to consider what to include here 
    # for instance if first word is HIGHLIGHTS we know there are various news items in this article 
        
    # so we should only include those from same section.
    rules = {"all_caps_as_new_paragraph"}    
    #ent = dis_entities['PERSON'][starting_politician]     #THIS SHOWS THAT ORIGINALLY I WAS ONLY GETTING RELATIONS INVOLVING CENTRAL NODE AND NOT OTHERS.
    start_tag = ""
    for t, tels in dis_entities.iteritems():
	for tentname, tentdata in tels.iteritems():
		if tentname == starting_politician:
			start_tag = t
			break	

    try:
    	ent = dis_entities[start_tag][starting_politician]
    except:
	traceback.print_exc(file=sys.stdout)
	printflush("ERROR: COULDN'T FIND ENT with start_tag: "+str(start_tag)+" and starting_politician: "+str(starting_politician))
	printflush("Starting Politician maybe got merged over incorrectly.. here are disentities: ")
	printflush(dis_entities)
	
    
    res = []
    num_inst = len(ent['sentence'])
    
    if debug:
        printflush("In Get Relations\n"+start_tag+": "+starting_politician+"\nEntities")
        printflush(entities)
        printflush("\nDisambiguated")
        printflush(dis_entities)
        printflush("\nSentences")
        printflush(sentences)
        printflush("Ent")
        printflush(ent)
	printflush("NUM_INST= "+str(num_inst)+"... this is the number of loops @@@@@@ that you'll see\n\n")
    
    i = 0
    sent_matches = []
    
    #TODO make sure you aren't double counting anything!
    while i < num_inst:        
        #sent_num = ent['id'][i]
        sent_num = ent['sentence'][i]
        sent = sentences[sent_num]
        if debug:
            printflush("@@@@@@Working on match from sentence "+str(sent_num))
            printflush(sent)
            
        #get entities in same sentence and add to res
        same_sent = get_entities_for_sentence(sent_num,dis_entities,False)  #instead of debug
        if debug:
            printflush("ENTITIES IN SAME SENTENCE")
            for s in same_sent:
                printflush(s)
            
        #get entities in surrounding three sentences
        prior_sents, next_sents = get_entities_for_surrounding_sentences(sent_num,dis_entities,len(sentences)-1,debug)
        if debug:
            printflush("\nPRIOR "+ str(number_sentences_for_context)+" sentences")
            for p in prior_sents:
                printflush(p)
            printflush("\nNEXT "+ str(number_sentences_for_context)+" sentences")
            for ns in next_sents:
                printflush(ns)
            
        #get entities in same article 
        prior_far, next_far = get_entities_further_away_in_article(sent_num,dis_entities,len(sentences)-1,debug)
        if debug:
            printflush("\n\nPRIOR FARTHER THAN "+ str(number_sentences_for_context)+" sentences" )
            for pf in prior_far:
                printflush(pf)
            printflush("\nNEXT FARTHER THAN " + str(number_sentences_for_context)+" sentences")
            for nf in next_far:
                printflush(nf)
        
        if num_inst == 1:
            res = [same_sent, prior_sents, next_sents, prior_far, next_far]
        else:
            res.append([same_sent, prior_sents, next_sents, prior_far, next_far])
        i = i + 1
                
    return [ent['sentence'], res]


def get_ent_to_global(dis_entities,debug):
    global global_index
    ent = {}
    ent_to_global = {}    
    
    for r in dis_entities:
        for e in dis_entities[r]:
            cur = dis_entities[r][e]
            cur["entity_type"] = r
            ent[e] = cur
            
            #see if current entity exists in global list
            if debug:
                printflush("\nChecking if "+e+" is in global index")
                
            if e in global_index:
                ent_to_global[e] = global_index[e]                
                if debug:
                    printflush("\tFound in global index\nTODO VERIFY CORRECT:\nGlobal:")
                    printflush(global_entities[ent_to_global[e]])                                               
                    printflush("\nvs Local:")
                    printflush(cur)
            else:
                if debug:
                    printflush("\tNot found directly in global index so check for something similar")
                
                handled = 0
                for ge in global_index:                    
                    if e.lower() == ge.lower():
                        if debug:
                            printflush("\tFound "+ge+" which is equal lowercase wise and using it as entity")
                        ent_to_global[e] = global_index[ge]
                        handled = 1
                        break
                    else:
                        if e in ge:                         
                            if debug:
                                printflush("\tNow: Found for something which subsumes it: "+ge)
                                printflush("\tTODO:  check if they have same type, and are same. Don't do for locations.  this must be failsafe.. \nGlobal:")
                                printflush(global_entities[global_index[ge]])
                                printflush("\nvs Local:")
                                printflush(cur)
                            
                            if (global_entities[global_index[ge]]['entity_type'] == cur['entity_type'] 
                                or global_entities[global_index[ge]]['entity_type'] == "politician" )and cur['entity_type'] == "PERSON":
                                if debug:
                                    printflush("\tFound these two to be the same entity!")
                                handled = 1
                                ent_to_global[e] = global_index[ge]
                                break
                    
                if handled == 0:
                    if debug:
                        printflush("\tDid not find "+e+" in global index so add it")
                        printflush(cur)
                    cur["full_name"] = e
                    global_entities.append(cur)
                    global_index[e] = len(global_entities) - 1
                    ent_to_global[e] = global_index[e]
                        
    if debug:
        printflush("ENT:")
        printflush(ent)
        printflush("\nENT_TO_GLOBAL:")
        printflush(ent_to_global)
        
    return [ent_to_global,ent]
