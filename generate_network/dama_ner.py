from dama_utils import *
#initialize Named Entity Recognition engine
import sys, os, string

#GLOBAL VAR
mitiepath = "/Users/dolano/htdocs/dama-larca/mitie/MITIE-master/"
sys.path.append(mitiepath+"mitielib")

from mitie import *
from collections import defaultdict

ner = named_entity_extractor(mitiepath+'MITIE-models/english/ner_model.dat')

def get_entities_details(tokens,entities,debug=False):    
    reso = []
    for e in entities:
        range = e[0]
        tag = e[1]
        score = e[2]
        score_text = "{:0.3f}".format(score)
        entity_text = " ".join(tokens[i] for i in range)
        if debug == True:
            printflush("\t\tScore: " + score_text + ": " + tag + ": " + entity_text    )
        reso.append({'score': score_text, 'tag': tag, 'text': entity_text})
    
    return reso    
    
def get_named_entities_per_sentence(sentences,debug=False):
    #TODO make this return entities in the order in which they appear in the sentence
    res = []
    if debug:
        printflush("\nIn Get named entities per sentence!")
    for i,s in enumerate(sentences):
        try:
	    
            tokens = tokenize(s)            
            entities = ner.extract_entities(tokens)      
            if debug == True:
                printflush("\nSentence: " + s)
                
            ret = get_entities_details(tokens,entities,debug)
            res.append(ret)   
        except:
            if debug == True:
                printflush("ERROR: can not tokenize as is so removing ascii characters")
            news = filter(lambda x: x in string.printable, s)
	    sentences[i] = news    #fix this sentence for future use in other functions!
            try:
                tokens = tokenize(news)            
                entities = ner.extract_entities(tokens)      
                if debug == True:
                    printflush("\nSentence: " + news)
                
                ret = get_entities_details(tokens,entities,debug)
                res.append(ret)   
            except:
                printflush("SUPER ERROR - couldn't tokenize as is or without ascii characters" + s)
                return []    

    return [res,sentences]

def verify_entity_found(entities,name,debug=False):
    #[[{u'text': u'AUSTIN', u'score': 0.8039498955658273, u'tag': 'LOCATION'}, 
      #{u'text': u'Texas House', u'score': 1.0538336421043815, u'tag': 'LOCATION'}], 
     #[{u'text': u'House', u'score': 0.6314707951634598, u'tag': 'ORGANIZATION'}, 
      #{u'text': u'Texas Lottery Commission', u'score': 1.254348992018721, u'tag': 'ORGANIZATION'}], [....]]
    ret = False
    #es = [a['text'] for a in e for e in entities]
    es = []
    for e in entities:
        for a in e:
            if a['text'] not in es:
                es.append(a['text'])
                
    if name in es:
        ret =True
    else:
	if name.upper in es:
		if debug: printflush("ALL UPPERCASE VERSION OF ENTITY FOUND SO FIX IN ENTITIES")
		ret = True
		#update entity if all upper case version found!
		for i,s in enumerate(entities):
			for a,e in enumerate(s):
				if e['text'] == name.upper:
					entities[i][a]['text'] = name
	else:
		for i,s in enumerate(entities):
			for a,e in enumerate(s):
				if name in e['text']:
					if debug: printflush("\t\t\tFound "+name+" in "+e['text'] + "with tag: "+e['tag'])
					entities[i][a]['text'] = name
					if entities[i][a]['tag'] == 'LOCATION' or entities[i][a]['tag'] == 'ORGANIZATION':
						entities[i][a]['tag'] = "PERSON" 
					ret = True
    return [entities,ret]


def entity_in_list(ent,li):
    entl = ent.lower()
    ret = [False,""]
    for l in li:
        if entl == l.lower():
            ret = [True,l]
            break
    return ret


#####THIS IS THE BIG BAD ENTITY FINDING FUNCTION########################

@timeout(15)
def disambiguate_entities(entities,sentences,db,debug=False):
    #TODO pull out big sections into seperate functions
    if debug:
        printflush("Function: In Disambiguate Entities")
        printflush("Sentences: ")
        printflush(" ".join(sentences))
        printflush("Entities")
	for ets in entities:
        	printflush(ets)
    
    #TODO        
    res = {'ORGANIZATION':{},'PERSON':{},'LOCATION':{},'MISC':{},'BILL':{}}
    titles = ["Governor","Lieutenant Governor","Gov","Representative","Rep","REP","Senator","Sen","Commissioner","House Speaker","Speaker", "Chairman","Chairwoman", "Judge", "Member","member","Trustee","trustee","President","president","Lawyer", "lawyer","Candidate","incumbent","Incumbent","challenger","businessman","State Representative","State Rep"]
    
    naive_coref = []
    local_id = 0
    prior_seen_objs = []
    prior = {"text":"","tag":"MISC"}
    cur_sen = 0
    skip = 0
    for sent in entities:
	if debug: 
		printflush("Now on sentence:") 
		printflush(sent)

        for ind,e in enumerate(sent):
	    if debug:  printflush("Currently on "+str(e))
            if skip == 1:
                #skip when the post word has been accounted for MAYBYE   #NO NO NO  right?
                skip = 0
                if debug:
                    printflush("Skipping " + e['text'] + " as its already been added in prior step!")
                continue
                
            t = e['text']
            tlower = t.lower()
            already_in, tswap = entity_in_list(t,res[e['tag']])
            if already_in:
                t = tswap
                #print "TODO " + t + ' already in so give it same token'                
                res[e['tag']][t]['id'].append(local_id)
                res[e['tag']][t]['sentence'].append(cur_sen)
            else:
                #TODO INCORPORATE FUZZY AND 
                #ALSO LOOK FOR PRIOR ENTITY IN FRONT OF PEOPLE, so we can find roles better
                if t.find('D-') == 0 or t.find('R-') == 0:
                    #found a clear sign that the prior (mostly likely) or next (unlikely) entity is a politician
                    #print "Found possible politician "+t+" so look at prior"
                    #print prior
                    
                    ps = t.split('-')
                    party = "Republican" if ps[0] == 'R' else "Democrat"
                    loc = ps[1]   
                    pt = prior['text']
                    if pt in res[prior['tag']]:
                        if debug:
                            printflush("Found D- or R- with "+t+" , now adding party: "+party+" and maybe location: "+loc)
                            
                        res[prior['tag']][pt]["party"] = party 

			if loc in res['LOCATION']:			
                        	res[prior['tag']][pt]["location"] = loc
			else:
				#based on article 463 for Bob Hall
				#http://www.dallasnews.com/opinion/editorials/20150112-editorial-some-advice-to-north-texas-freshman-lawmakers-as-legislature-opens.ece
				if debug: printflush("Didn't find "+loc+" in LOCATION but check if first word of it is.. in which case assume that the rest is a person tag you should add!!")
				locps = loc.split(" ")
				if len(locps) > 1:
					newloc = locps[0]
					pers = " ".join(locps[1:len(locps)])
					
					
					if newloc in res['LOCATION']:
						if debug: printflush("FOUND NEW LOCATION: "+newloc+" in priors so add it to prior person")
                        			res[prior['tag']][pt]["location"] = newloc
						
						#CHECK if pers exists in PERSON already and if so append, otherwise add
						if pers in res['PERSON']:
							res['PERSON'][pers]['id'].append(local_id)
							res['PERSON'][pers]['sentence'].append(cur_sen)
						else:
							if debug: printflush("ADD PERSON: "+pers+" to res at sentence: "+str(cur_sen))
							res['PERSON'][pers]= {'id':[local_id], 'sentence':[cur_sen]}                    
						
						
				
                    else:
			#for cpt in res[prior['tag']]:
			#	if pt in cpt:
	
                        if debug:
                            printflush("hmmmERROR! Did not find "+pt+" with tag "+prior['tag']+", in results list")
			    printflush("RES:")
                            printflush(res)
			    #printflush("SENTENCES CURRENT SEN:")
                            #printflush(sentences[cur_sen])
			    printflush("Maybe its second part is the Name we are looking for")
                            #printflush("TODO SEE IF PRIOR WORDS are Uppercased and just weren't considered as an Entity and use them")
			    
			perps = pt.split(" ")
			if len(perps) > 1:
				pre = perps[0]
				#newloc = pre.split("-")[1]
				priorpers = " ".join(perps[1:len(perps)])
				#CHECK if pers exists in PERSON already and if so append, otherwise add
				if debug: printflush("Looking for "+priorpers+" in RES above\n");
				if priorpers in res['PERSON']:
					if debug: printflush("Found person")
                        		res['PERSON'][priorpers]["party"] = party 
					locps = loc.split(" ")
					if debug: printflush(locps)
					if len(locps) > 1:
						newloc = locps[0]
						pers = " ".join(locps[1:len(locps)])
						if newloc in res['LOCATION']:
							if debug: printflush("FOUND NEW LOCATION: "+newloc+" in priors so add it to prior person")
							res['PERSON'][priorpers]["location"] = newloc

							#CHECK if pers exists in PERSON already and if so append, otherwise add
							if pers in res['PERSON']:
								res['PERSON'][pers]['id'].append(local_id)
								res['PERSON'][pers]['sentence'].append(cur_sen)
							else:
								if debug: printflush("ADD PERSON: "+pers+" to res at sentence: "+str(cur_sen))
								res['PERSON'][pers]= {'id':[local_id], 'sentence':[cur_sen]}                    
				else:
					nothingtodo = 1

			#maybe its the case that the current word has R-DALLAS but that that politician thing is for prior perso
			#Of 24 members new to the House, these are from North Texas:
			#Linda Koop, R-Dallas
			#Morgan Meyer, R-Dallas
			#Matt Rinaldi, R-Irving
			#Ramon Romero, D-Fort Worth

                        #break
                    
                elif tlower == 'senate bill' or tlower == 'house bill':
                    #possible bill so find location in sentence and include number of bill                    
                    ps = sentences[cur_sen].split()
                    if debug:
                        printflush("Found Senate or House Bill")
                        printflush(ps)
                        
                    for i, j in enumerate(ps):        
                        if j == 'Bill' or j == 'bill':
                            if debug:
                                printflush("*Found "+j+" "+str(ps[i+1]))
                            
                            bb = ps[i+1].replace(":","")
                            
                            if is_number(bb) == True:
                                if debug:
                                    printflush("numeric")
                                bill = ps[i-1]+" " +ps[i]+" "+bb
                                if debug:
                                    printflush("Found bill: " + bill)
                                res['BILL'][bill] = {'id':[local_id], 'sentence':[cur_sen]}

                                
                elif t == 'SB' or t =='HR' or t =='HB':
                    #possible bill so find location in sentence and include number of bill                    
                    ps = sentences[cur_sen].split()
                    if debug:
                        printflush("FOUND SB/HR/HB!")
                        printflush(ps)
                        
                    for i, j in enumerate(ps):        
                        if j == 'SB' or j == 'HR' or j == 'HB':
                            bb = ps[i+1].replace(":","")
                            if is_number(bb):
                                bill = ps[i]+" "+bb
                                if bill in res['BILL']:
                                    if debug:                                    
                                        printflush("Found bill already")
                                        printflush(bill)
                                    res['BILL'][bill]['id'].append(local_id)
                                    res['BILL'][bill]['sentence'].append(cur_sen)
                                    
                                elif "House Bill "+bb in res['BILL'] or "Senate Bill "+bb in res['BILL']:
                                    if debug:
                                        printflush("TODO found bill already so add to alias of it")
                                    if "House Bill "+bb in res['BILL']:
                                        res['BILL']["House Bill "+bb]['id'].append(local_id)
                                        res['BILL']["House Bill "+bb]['sentence'].append(cur_sen)
                                    else:
                                        res['BILL']["Senate Bill "+bb]['id'].append(local_id)
                                        res['BILL']["Senate Bill "+bb]['sentence'].append(cur_sen)                                        
                                else:   
                                    if debug:
                                        printflush("ADD Bill"+bill+" to res")
                                    res['BILL'][bill] = {'id':[local_id], 'sentence':[cur_sen]}
                                    
                elif e['tag'] == "PERSON":
                    #check that this person is definitely not already in res 
                    #TODO: ( this only works if full name appears before single) 
                    #     thus, at end we'll have to fuzzy combine of PERSON list , and for ORGANIZATION list
                    # TODO EVENTUALLY USE DBPEDIA to verify
                    found = 0
                    if len(t.split()) == 1:
                        #check if this last name                        
                        for i, j in enumerate(res['PERSON']):        
                            if t in j:
                                if debug: 
                                    printflush("Found name in PERSON ALREADY"+t+" in "+j)  #BECAREFUL HERE, this is too broad
                                res['PERSON'][j]['id'].append(local_id)
                                res['PERSON'][j]['sentence'].append(cur_sen)
                                found = 1
                        
                        if found == 0:
                            if debug:
                                printflush("FOUND PERSON: "+t+", but as its of size 1, we don't add by default" )
                            #
                            #Check to see if there is another name after or before
                            #res['PERSON'][t] = {'id':[local_id], 'sentence': [cur_sen]}

                                
                    elif len(sent) > ind + 1:                                                   
                        #check if next entity in sentence is a location and if the are combined by "of" or "from"
                        next_ent = sent[ind + 1]
                        ff = 0
                        if next_ent['tag'] == 'LOCATION':
                            start = sentences[cur_sen].find(e['text'])
                            end = sentences[cur_sen].find(next_ent['text'])
                            if end > start:
                                ps = sentences[cur_sen][start+len(e['text']):end].split()
                                if len(ps) == 1:
                                    if ps[0] == "of" or ps[0] == "from":
                                        res[e['tag']][t]= {'id':[local_id],'location':next_ent['text'], 'sentence':[cur_sen]}
                                        ff = 1
                        if ff == 0:
                            res[e['tag']][t]= {'id':[local_id],'sentence':[cur_sen] }
                                                                   
                    else:
                        #if debug == debug:
                        #    printflush("ADD PERSON: "+t+" to res at sentence: "+str(cur_sen))
                        res[e['tag']][t]= {'id':[local_id], 'sentence':[cur_sen]}                    

                    #LOOK FOR Governor, Represenative, Rep, Senator, Commisioner, etc in word before and 
                    #if so add, and check that is not already and an entity, etc                    
                    ps = sentences[cur_sen].split()
                    
                    check = t    
                    if len(t.split()) > 1:
                        check = t.split()[0]
                        
                    if debug:
                        printflush("\nAAAAAA: Looking if word prior to PERSON "+t+ " is a title")
                        printflush("Check is: "+check)
                        printflush(ps)
                       
                    #does this handle case 47? with Jessica Farrer and then Farrer after
                    found_once = 0 
                    found_at = -1
                    for i,c in enumerate(ps):
                        if (c == check or (c.replace("'s","").replace(":","").replace(',','') == check)) and found_once == 0:
                            found_at = i
                            if len(t.split()) > 1:
                                #verify actually have correct person when Joe Wilson and Joe Matts in same sentence
                                if len(ps) > i +1:
                                    if ps[i+1].replace(":","").replace(",","").replace(".","").replace("?","").replace("'s","") != t.split()[1]:
                                        found_at = -1
                                        if debug:
                                            printflush("Found false match: "+ps[i]+" "+ps[i+1]+" vs "+t+" so continue to see if you find it")
                                        continue
                                                                       
                            found_once = 1
                            if debug:
                                printflush("Found "+c+" at index: "+str(i)+"and now checking for type")
                            
                            if ps[i-1] in titles:
                                pos_title = ps[i-1]
                                if ps[i-2]+" "+ps[i-1] in titles:
                                    pos_title = ps[i-2]+" "+ps[i-1]
                                    
                                if debug:
                                    printflush("FOUND TITLE "+ pos_title)
                                    printflush("look in prior: "+prior['text'])
                                    
                                #TODO: MAKE THIS GO FARTHER BACK THAN JUST ONE WORD 
                                #  if the one before is CAPS or part of the prior entity which is an ORG    
                                #  in which case add org + ps[-1] as position, and remove org from res entities
                                
                                #TODO: make this also check next word, ex.  Jim Moon, president of Conoco
                                if 'text' in prior:
                                    if pos_title in prior['text']:
                                        #look if title is part of prior entity
                                        if t in e['tag']:
                                            res[e['tag']][t]['position'] = [prior['text']]
                                        elif t.replace(",","") in e['tag']:
                                            res[e['tag']][t.replace(",","")]['position'] = [prior['text']]
                                        elif prior['text'] in titles:
                                            res[e['tag']][t]['position'] = [prior['text']]
					elif prior['text'].split(" ")[-1] in titles:
					    try:
                                            	res[e['tag']][t]['position'] = [prior['text']]
					    except:
						if debug: printflush("ERROR, with index "+t)
					else:
                                            if debug: printflush("ERROR, didn't find: "+t+" in "+prior['text']+", pos_title= "+pos_title+" is it a punctuation thing?")
					    #printflush(e['tag'])
					    #printflush(res)
                                        
                                        #and then remove prior entity
                                        if prior['text'] in res[prior['tag']]:
                                            if debug:
                                                printflush("prior[text]: "+prior['text'])
                                                printflush("prior[tag]:")
                                                printflush(res[prior['tag']])
                                                printflush("Deletion successfull")
                                            #res[prior['tag']].remove(prior['text'])
                                            del res[prior['tag']][prior['text']]
                                        else:
                                            if debug:
                                                printflush("ERROR didn't find prior text: "+prior['text']+" with tag: "+prior['tag']+" in res")
                                                printflush("This means it didn't get inserted properly before, so look into it")
                                    else:
                                        if t in res[e['tag']]:
                                            if debug:
                                                printflush("Add position: "+pos_title+" to "+t)
                                            res[e['tag']][t]['position'] = [pos_title] 
                                        else:
                                            if debug:
                                                printflush(t+" not found in local res so either check in globals(TODO) or just add?")
                                                printflush("For now just add PERSON: "+t+" with position "+pos_title)
                                            res["PERSON"][t]= {'id':[local_id], 'sentence':[cur_sen], 'position':[pos_title] }
                                            
                                else:
                                    #otherwise just use prior word as title
                                    res[e['tag']][t]['position'] = [pos_title]
                            else:
                                #if prior word is in prior entity which is a one named PERSON, 
                                #how to handle: Representative Inocente "Chente" Quintanilla
                                if debug:
                                    printflush("At: "+str(i)+"Check if "+ps[i-1]+" is same person entity as prior words.  Current Sentence:")
                                    printflush(ps)
                                    printflush("Prior word (if any)"+ str(prior))
                                    printflush("TODO: check if prior capitalized words in conjugation with this one is in Global Entities as a PERSON")
                                    printflush("OR BETTER, just keep check if prior words are Caps and you eventually run into a title" )
                                    printflush(ps[i-1].replace('"','') in prior['text'])
                                    printflush((prior['tag'] == 'PERSON' or prior['tag'] == 'MISC'))
                                    printflush(str(len(prior['text'].split())))
                                    
                                if i == 0:
                                    if debug:
                                        printflush("Index is at 0 so there is no prior title, so skip")
                                    continue
                                if ps[i-1] == '"':
                                    if debug:
                                        printflush('Found " so skip it!-- TODO handle this better')
                                    continue
                                    
                                if ps[i-1].replace('"','') in prior['text'] and (prior['tag'] == 'PERSON' or prior['tag'] == 'MISC') and len(prior['text'].split()) == 1:                                                                        
                                    if debug:
                                        printflush("????FOUND possible names that should be combined: "+prior['text']+" and "+t)                                     
                                        #TODO  (doublecheck)!!!  
                                        #which was not found in res already (ie, it was added to prior object)                                                                        
                                        printflush(res)
                                        printflush(prior_seen_objs)
                                        
                                    #combine the prior PERSON and this person into ONE, if this person is of size one
                                    if prior['text']+" "+t in res['PERSON']:
                                        if debug:
                                            printflush(prior['text']+" "+t+" already in index so do nothing")
                                    else:
                                        if debug:
                                            printflush(prior['text']+" "+t+" added to index")
                                            printflush("Delete "+prior['text']+" of tag("+prior['tag']+") from index")

                                        #Add to index, and set this current res, e'text' to t so that its set as prior at end
                                        t = prior['text']+" "+t
                                        res['PERSON'][t] = {'id':[local_id], 'sentence': [cur_sen]}
                                        e['text'] = t
                                        
                                        if prior['text'] in res[prior['tag']]:
                                            if debug:
                                                printflush("Deletion successfull")
                                            del res[prior['tag']][prior['text']]
                                    
                                elif ps[i-1].replace('"','')[0].isupper() and ps[i-1].replace('"','') not in prior['text']:
                                    if debug:
                                        printflush("TODO: prior word "+ps[i-1]+" is uppercase and not an entity or title.  These be combined only if a title is found priorly eventually !")
                                        
                                elif ps[i-1] == "Democrat" or ps[i-1] == "Republican":
                                    if debug:
                                        printflush("Not title, but yes Democrat/Republican so add")
				    try:
                                    	res[e['tag']][t]['party'] = [ps[i-1]]
				    except:
					if debug: printflush("Error getting party for "+t)
                                    
                elif e['tag'] == 'ORGANIZATION' and t.split()[-1].lower() == "district":
                    #look to see if this like Texas House District 133, 
                    if debug:
                        printflush("Check if ORG: "+t+ ", is followed by a number")
                    loc = sentences[cur_sen].find(t)
                    if loc > -1:
                        loc = loc + len(t)
                        possible_num = sentences[cur_sen][loc:].split()[0]
                        possible_num = possible_num.replace(":","").replace(",","")
                        if is_number(possible_num):
                            if debug:
                                printflush("Found District "+possible_num)
                            t = t + " " + possible_num
                    
                    res[e['tag']][t]= {'id':[local_id], 'sentence':[cur_sen]}                        
                
                elif e['tag'] == 'LOCATION':
                    #look to see if next word is in upper case,
                    ps = sentences[cur_sen].split()
                    
                    if t.split()[-1].lower() == "district":
                        if debug:
                            printflush("Check if LOCATION: "+t+ ", is followed by a number")
                        loc = sentences[cur_sen].find(t)
                        if loc > -1:
                            loc = loc + len(t)
                            possible_num = sentences[cur_sen][loc:].split()[0]
                            possible_num = possible_num.replace(":","").replace(",","")
                            if debug:
                                printflush("Found "+t+" at position "+str(loc))
                                printflush("Check if "+possible_num+" is a number")
                                
                            if is_number(possible_num):
                                if debug:
                                    printflush("Found District "+possible_num)
                                t = t + " " + possible_num
                                #treat Districts as Organizations (maybe incorrect, but consistent)
                                res["ORGANIZATION"][t]= {'id':[local_id], 'sentence':[cur_sen]} 
                                continue
                        
                    if debug:
                        printflush("\nAAAAAA: Looking if word after LOCATION "+t+ " is in CAPS and part of an ORGANIZATION NAME")
                        printflush(ps)
                       
                    check = t    
                    if len(t.split()) > 1:
                        check = t.split()[-1]
                    
                    if debug:
                        printflush("check is "+check)
                        
                    added = 0
                    found_once = 0
                    for i,c in enumerate(ps):
                        if c == check and found_once == 0:
                            if len(t.split()) > 1:
                                #verify actually have correct location when two have same starting word in sentence
                                if i+1 >= len(ps):
                                    #to fix error with a=189 (where last word in sentenc is Location)
                                    continue
                                    
                                if ps[i+1].replace(":","").replace(",","") != t.split()[1]:
                                    continue
                                    
                            found_once = 1
                            if debug:
                                printflush("FOUND C = CHECK")
                            if len(ps)-1 > i:
                                start = 1
                                if debug:
                                    printflush("NOW CHECK IF "+ps[i+start]+ " is upper or stopword(TODO)")  #of, at, and, &   
                                if ps[i+start][0].isupper():
                                    possible_add = ps[i] + " " + ps[i+start]
                                    if debug:
                                        printflush("Found "+ps[i+start]+ " which is uppercase")
                                    if len(sent) - 1 > ind:
                                        next_ent = sent[ind + 1]
                                        next_front = next_ent['text']
                                        if len(next_ent['text'].split()) > 1:
                                            next_front = next_ent['text'].split()[0]
                                            
                                        if next_front != ps[i+1]:
                                            if debug:
                                                printflush('Next front: '+next_front+' not equal to '+ps[i+1])
                                            start = start + 1
                                            exit = 0
                                            while i + start < len(ps) and start < 5 and exit ==0:
                                                if ps[i+start][0].isupper() and ps[i+start] != next_front and start < 5:
                                                    possible_add = possible_add + " " + ps[i+start]
                                                
                                                if ps[i+start] == next_front:
                                                    exit = 1
                                                    
                                                start = start + 1
                                                
                                                
                                            if debug:
                                                printflush("EEEEE Possible ROLE/ORGANIZATION FOUND: " + possible_add)
                                                printflush("Next entity is a "+next_ent['tag'] + " and last = " + possible_add.split()[-1])
                                                
                                            if next_ent['tag'] == 'PERSON' and possible_add.split()[-1] in titles:
                                                if debug:
                                                    printflush("PLACE THE PRIOR AS ROLE FOR "+next_ent['text'])
                                                    #check if PERSON entity already in res
                                                    f = 0
                                                    
                                                    for i, j in enumerate(res['PERSON']): 
                                                        if j == next_ent['text']:                                                            
                                                            #add role to that user
                                                            if 'position' in res['PERSON'][j]:
                                                                res['PERSON'][j]['position'].append(possible_add)
                                                            else:
                                                                res['PERSON'][j]['position'] = [possible_add]
                                                            f = 1
                                                            added = 1
                                                        else:
                                                            if len(next_ent['text'].split()) == 1:
                                                                if next_ent['text'] in j:
                                                                    #add role to user
                                                                    if 'position' in res['PERSON'][j]:
                                                                        res['PERSON'][j]['position'].append(possible_add)
                                                                    else:
                                                                        res['PERSON'][j]['position'] = [possible_add]
                                                                    f = 1  
                                                                    added = 1
                                                    if f == 0:
                                                        skip = 1
                                                        if debug:
                                                            printflush("PERSON NOT FOUND IN RES so add along with position and then skip when it comes up!")
                                                        res['PERSON'][next_ent['text']]= {'id':[local_id], 'sentence':[cur_sen], 'position': [possible_add]}
                                                        added = 1
                                            else:
                                                if debug:
                                                    printflush("TODO next is not a person so add " + possible_add + " as ORG")
                                                    res['ORGANIZATION'][possible_add]= {'id':[local_id], 'sentence':[cur_sen]}
                            
                    if added == 0:
                            res[e['tag']][t]= {'id':[local_id], 'sentence':[cur_sen]}
                    #if so take all next words which are in uppercase and aren't part of the next entity for the line
                else:
                    res[e['tag']][t]= {'id':[local_id], 'sentence':[cur_sen]}
                    
            local_id = local_id + 1
            prior = e
            prior_seen_objs.append(prior)
        cur_sen = cur_sen + 1
    
    if debug:
        printflush("\nEnd Results for Function: Disamb")
        printflush(res)

    return res



