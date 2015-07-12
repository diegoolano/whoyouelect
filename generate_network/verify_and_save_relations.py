from dama_globals import *
from dama_utils import *
from entity_funcs import *
from dama_ner import *
from handle_funcs import *
import sys
import string
import time
import copy
import traceback

def generate_url_list():
    #make url list indexed by mongoid so that edges just need mongoid to show id
    global global_relations
    for i,gr in enumerate(global_relations):
        mongoid = str(global_relations[gr]['mongoid'])
	mongoid = mongoid.replace("ObjectId(","").replace(")",'')   #NEW
        url_list[mongoid] = {'url':global_relations[gr]['url'], 'date': global_relations[gr]['date'],
                             'num_sentences':global_relations[gr]['num_sentences'], 
                             'entities':len(global_relations[gr]['entities']),
                             'relations':len(global_relations[gr]['relations'])}

def get_global_entity_by_name(name):
	global global_entities
	for i,p in enumerate(global_entities):
		if p["full_name"] == name:
			return [i,p]
	return [-1,[]]


def get_local_index(queryobj,ent,debug):
    if queryobj[1] in ent:
        loc_index = queryobj[1]
    else:
        if debug:
            printflush("ERROR: didn't find "+queryobj[1]+" in entity list above so find closest approximation")
        for e in ent:
            if queryobj[1].lower() in e.lower():
                loc_index = e
                break
    return loc_index

 
def normalize(s):
	for p in string.punctuation:
		s = s.replace(p, '')
	return s.lower().strip()

def filter_entities(dis_entities,centernode,debug):
	if debug:
		printflush("In Filter Entities with dis_entities")
		printflush(dis_entities)
        	filter_start = time.clock()


	exclude = ["Democrats","Democratic","Democrat","Houston Democrat","Houston Democrats","House Democratic","Houston-area","Houston Democratic","Democratic Representatives",
		   "Republican","Republicans","Republican House","GOP","Republican Party","Justice","US","Texans","Houstonians","House Republicans",
		   "House","two House","House floor","Senate","Congress","Texas Legislature","Legislature","Chronicle","State Senate","House Aug","Legislative",
		   "House of Representatives","House Majority","Houston Chronicle","The Chronicle","Democrat Garnet Coleman","Obama Clinton",
		   "American","janet .","chris .","Internet","University","The House","P.O.","contrast Bell","Council","Colemans","America","U.S.","United States", "US", "USA",
		   "Democrats Craddick","Tier","chairmen Pitts","Texas-Mexico","African-American","Capital",
		   "Walt","Congressman Ryan","ID","Montessori","Bills","Taser","Tasers","Subscribe","CDATA","Relevance","Texas"]

	to_delete = {}
	to_keep = {}
	for t in dis_entities:                 
		td = []
		tk = []
		for f in dis_entities[t]:
			if f in exclude or len(normalize(f)) < 3:
				td.append(f)
			else:
				tk.append(f)
		to_delete[t] = td
		to_keep[t] = tk
					

	if debug:
		print "To Delete Based on Exclude List or being of size 2 or below"
		print to_delete

	for tde in to_delete:
		for e in to_delete[tde]:
			del dis_entities[tde][e]

	if debug:
		printflush("After Exclude (and before merge), dis_entities")
		printflush(dis_entities)

	##NOW REMOVE BY MERGING ( if two words are 95% the same, merge them into one! )
	to_merge = {}
	seen = {}
	for t in to_keep:
		to_merge[t] = {}
		seen[t] = []
		for tt in to_keep[t]:
			 ttn = normalize(tt)	
			 tmp = [ to for to in to_keep[t] if to != tt and normalize(to) == ttn and to not in seen[t]] 
			 if tmp != []:
				if debug:
					print "For "+tt+" found items to merge with "+",".join(tmp)
				to_merge[t][tt] = tmp
				seen[t].append(tt) # this was seen.append(tt)
				for m in tmp: seen[t].append(m)

	if debug:
		printflush("TO MERGE")
		printflush(to_merge)
		printflush("Seen")
		printflush(seen)

	#NOW DO MERGING ON DIS_ENTITIES BASED ON to_merge (this is simple since we don't allow for merging across Entity Types)
	for t in to_merge:
		for tm in to_merge[t]:
			for tdm in to_merge[t][tm]:
				try:
					del dis_entities[t][tm]
				except:
					if debug: print("error deleting "+tm+" and tdm? "+tdm) 
	
	'''
	ORGANIZATION
		Straus and Company : {'id': [22], 'sentence': [19]}
		Texas Tribune : {'id': [1], 'sentence': [0]}
		Tribune : {'id': [2], 'sentence': [0]}
		Numbers Gives House Democrats : {'id': [51], 'sentence': [50]}
		Small Shift : {'id': [50], 'sentence': [50]}
		Mexican American Legislative Caucus : {'id': [46], 'sentence': [43]}
	BILL
	MISC
		Latinos : {'id': [36], 'sentence': [33]}
		Hispanic : {'id': [31], 'sentence': [32]}
	LOCATION
		Houston : {'id': [12], 'sentence': [9]}
		Relevance : {'id': [52], 'sentence': [50]}
		Dallas : {'id': [43], 'sentence': [38]}
		Straus : {'id': [17], 'sentence': [15]}
		Texas House : {'id': [4, 33], 'sentence': [1, 33]}
		Texas Democrats : {'id': [16], 'sentence': [12]}
		San Antonio : {'id': [14], 'sentence': [10]}
	PERSON
		Yvonne Davis : {'position': [u'Representative'], 'sentence': [38, 46], 'id': [42, 48], 'location': 'Dallas'}
		Trey Martinez Fischer : {'position': [u'Representative'], 'sentence': [10], 'id': [13], 'location': 'San Antonio'}
		Martinez Fischer : {'id': [45], 'sentence': [43]}
		Ross Ramsey : {'id': [0], 'sentence': [0]}
		Joe Straus : {'id': [3, 9, 19, 49], 'sentence': [1, 5, 17, 48]}
		Jessica Farrar : {'position': [u'Representative'], 'sentence': [9], 'id': [11], 'location': 'Houston'}
	'''
	#GIVEN EXAMPLE CASE ABOVE, 1) merge PERSONS who are subsumed by other PERSONS (in PERSON:  Trey Martinez Fischer should own Martinez Fischer )
	#			   2) merge LOCATIONS which are subsummed by PERSONS ( Straus should be Joe Straus )
	#			   3) merge ORGANIZATIONS which are subsummed by ORGANIZATIONS  	
	#			   4) merge LOCATIONS which are subsummed by ORGANIZATIONS (we are giving preference to Orgs over Locs)
	personnames = [ r for r in dis_entities["PERSON"]]
	seen = []	#1
	for p in personnames:
		check = [ pr for pr in personnames if pr != p and pr not in seen and p not in seen and (((p in pr) and p != centernode) or ((pr in p) and pr != centernode))]  #Don't merge over center person 
		if len(check) > 0: 
			if len(check) == 1:
				if debug: print "\t))))Found possible PERSON subsummed by another! either p: "+p+" is subsummed by pr: "+check[0]+" or viceversa"

				#HOW TO MERGE JUST ONE ANE ONE, DO I JUST NEED TO ADD ID of smaller into ID[] of other, and the same with sentence[] ?
				#TO AVOID John Whitmire is subsummed by pr: Democrat John Whitmire  or Democrat Hubert Vo is subsummed by pr: Hubert Vo or viceversa
				#Check if first word is Democrat or Republican				
				
				if p in check[0]:  #p subsummed by check[0] so copy p's ID and sentence into check[0]s
					if check[0].split(" ")[0].lower() in ["democrat","republican"]:
						#merge check[0] into p
						for i in dis_entities["PERSON"][check[0]]['id']:
							if i not in dis_entities["PERSON"][p]['id']: dis_entities["PERSON"][p]['id'].append(i)					
						dis_entities["PERSON"][p]['id'].sort()					
						for i in dis_entities["PERSON"][check[0]]['sentence']:
							if i not in dis_entities["PERSON"][p]['sentence']: dis_entities["PERSON"][p]['sentence'].append(i)					
						dis_entities["PERSON"][p]['sentence'].sort()					
						del dis_entities["PERSON"][check[0]]
					else:
						#merge p into check[0]
						for i in dis_entities["PERSON"][p]['id']:
							if i not in dis_entities["PERSON"][check[0]]['id']: dis_entities["PERSON"][check[0]]['id'].append(i)					
						dis_entities["PERSON"][check[0]]['id'].sort()					
						for i in dis_entities["PERSON"][p]['sentence']:
							if i not in dis_entities["PERSON"][check[0]]['sentence']: dis_entities["PERSON"][check[0]]['sentence'].append(i)	
						dis_entities["PERSON"][check[0]]['sentence'].sort()					
						del dis_entities["PERSON"][p]
				else: 
					if p.split(" ")[0].lower() in ["democrat","republican"]:
						#merge p into check[0]
						for i in dis_entities["PERSON"][p]['id']:
							if i not in dis_entities["PERSON"][check[0]]['id']: dis_entities["PERSON"][check[0]]['id'].append(i)					
						dis_entities["PERSON"][check[0]]['id'].sort()					
						for i in dis_entities["PERSON"][p]['sentence']:
							if i not in dis_entities["PERSON"][check[0]]['sentence']: dis_entities["PERSON"][check[0]]['sentence'].append(i)	
						dis_entities["PERSON"][check[0]]['sentence'].sort()					
						del dis_entities["PERSON"][p]
					else:
						#merge check[0] into p
						for i in dis_entities["PERSON"][check[0]]['id']:
							if i not in dis_entities["PERSON"][p]['id']: dis_entities["PERSON"][p]['id'].append(i)					
						dis_entities["PERSON"][p]['id'].sort()					
						for i in dis_entities["PERSON"][check[0]]['sentence']:
							if i not in dis_entities["PERSON"][p]['sentence']: dis_entities["PERSON"][p]['sentence'].append(i)					
						dis_entities["PERSON"][p]['sentence'].sort()					
						del dis_entities["PERSON"][check[0]]

					#TODO DO I NEED TO REMOVE THE DELETE ONE FROM GLOBAL anything global_index perhaps???? ie, are nodes that have been deleted still showing up in graph?

				seen.append(p)
				seen.append(check[0])
			else:
				if debug: print "\n!))))TODOFound possible PERSON subsummed by othersssss! either p: "+p+" is subsummed by pr: "+str(check)+" or viceversa"
				#TODO HOW TO MERGE THESE , look to see if this occurs !)))))  FOR NOW DON't
		else:
			check2 = [ pr for pr in personnames if pr != p and pr not in seen and p not in seen and (((p in pr) and p == centernode) or ((pr in p) and pr == centernode))]
			if len(check2) > 0:
				#allow for merge of Democrat Abel Herrero into Abel Herrero 
				if len(check2) == 1:
					if debug: print "\n))))Found possible MAIN PERSON subsummed by another! either p: "+p+" is subsummed by pr: "+check[0]+" or viceversa"

					if p in check2[0]:  #p is main person and is subsummed by p2.. we want to copy p2 into p so that we don't lose main node!
						for i in dis_entities["PERSON"][check2[0]]['id']:
							if i not in dis_entities["PERSON"][p]['id']:
								dis_entities["PERSON"][p]['id'].append(i)					
						dis_entities["PERSON"][p]['id'].sort()					

						for i in dis_entities["PERSON"][check2[0]]['sentence']:
							if i not in dis_entities["PERSON"][p]['sentence']:
								dis_entities["PERSON"][p]['sentence'].append(i)					
						dis_entities["PERSON"][p]['sentence'].sort()					
						del dis_entities["PERSON"][check2[0]]

					else:   #here p2 is main person which is subsummed by p... we want to copy p into p2 here so we don't lose main person
						for i in dis_entities["PERSON"][p]['id']:
							if i not in dis_entities["PERSON"][check2[0]]['id']:
								dis_entities["PERSON"][check2[0]]['id'].append(i)					
						dis_entities["PERSON"][check2[0]]['id'].sort()					

						for i in dis_entities["PERSON"][p]['sentence']:
							if i not in dis_entities["PERSON"][check2[0]]['sentence']:
								dis_entities["PERSON"][check2[0]]['sentence'].append(i)					
						dis_entities["PERSON"][check2[0]]['sentence'].sort()					

						del dis_entities["PERSON"][p]

					seen.append(p)
					seen.append(check2[0])
				
			else:
				seen.append(p)
	
	personnames = [ r for r in dis_entities["PERSON"]]
	locnames = [ r for r in dis_entities["LOCATION"]]  #2
	for p in locnames:
		check = [ pr for pr in personnames if pr != p and p in pr] 
		if len(check) > 0: 
			if debug:
				if len(check) == 1:
					print "\n))))Found possible LOCATION subsummed by PERSON! location p: "+p+" is subsummed by personr: "+check[0]
					if p in check[0]:  #p subsummed by check[0] so copy p's ID and sentence into check[0]s
						for i in dis_entities["LOCATION"][p]['id']:
							if i not in dis_entities["PERSON"][check[0]]['id']:
								dis_entities["PERSON"][check[0]]['id'].append(i)					
						dis_entities["PERSON"][check[0]]['id'].sort()					

						for i in dis_entities["LOCATION"][p]['sentence']:
							if i not in dis_entities["PERSON"][check[0]]['sentence']:
								dis_entities["PERSON"][check[0]]['sentence'].append(i)					
						dis_entities["PERSON"][check[0]]['sentence'].sort()					

						del dis_entities["LOCATION"][p]
						#TODO DO I NEED TO REMOVE THE DELETE ONE FROM GLOBAL anything global_index perhaps????
				else:
					print "\n!))))Found possible LOCATION subsummed by various PERSONS! LOC p: "+p+" is subsummed by pr: "+str(check)
					#TODO HOW TO MERGE THESE , look to see if this occurs !)))))
	

	orgnames = [ r for r in dis_entities["ORGANIZATION"]]  #3
	seen = []	#1
	for p in orgnames:
		check = [ pr for pr in orgnames if pr != p and pr not in seen and p not in seen and (p in pr or pr in p)] 
		if len(check) > 0: 
			if debug:
				if len(check) == 1:
					print "\n))))Found possible ORGANIZATION subsummed by another! either p: "+p+" is subsummed by pr: "+check[0]+" or viceversa"
					#HOW TO MERGE JUST ONE ANE ONE, DO I JUST NEED TO ADD ID of smaller into ID[] of other, and the same with sentence[] ?
					if p in check[0]:  #p subsummed by check[0] so copy p's ID and sentence into check[0]s
						for i in dis_entities["ORGANIZATION"][p]['id']:
							if i not in dis_entities["ORGANIZATION"][check[0]]['id']:
								dis_entities["ORGANIZATION"][check[0]]['id'].append(i)					
						dis_entities["ORGANIZATION"][check[0]]['id'].sort()					

						for i in dis_entities["ORGANIZATION"][p]['sentence']:
							if i not in dis_entities["ORGANIZATION"][check[0]]['sentence']:
								dis_entities["ORGANIZATION"][check[0]]['sentence'].append(i)					
						dis_entities["ORGANIZATION"][check[0]]['sentence'].sort()					

						del dis_entities["ORGANIZATION"][p]
					else: 
						for i in dis_entities["ORGANIZATION"][check[0]]['id']:
							if i not in dis_entities["ORGANIZATION"][p]['id']:
								dis_entities["ORGANIZATION"][p]['id'].append(i)					
						dis_entities["ORGANIZATION"][p]['id'].sort()					

						for i in dis_entities["ORGANIZATION"][check[0]]['sentence']:
							if i not in dis_entities["ORGANIZATION"][p]['sentence']:
								dis_entities["ORGANIZATION"][p]['sentence'].append(i)					
						dis_entities["ORGANIZATION"][p]['sentence'].sort()					
						del dis_entities["ORGANIZATION"][check[0]]

						#TODO DO I NEED TO REMOVE THE DELETE ONE FROM GLOBAL anything global_index perhaps????

					seen.append(p)
					seen.append(check[0])
				else:
					print "\n!))))Found possible ORGANIZATION subsummed by others! either p: "+p+" is subsummed by pr: "+str(check)+" or viceversa"
					#TODO HOW TO MERGE THESE , look to see if this occurs !)))))
		else:
			seen.append(p)

	orgnames = [ r for r in dis_entities["ORGANIZATION"]]
	locnames = [ r for r in dis_entities["LOCATION"]]  #4
	for p in locnames:
		check = [ pr for pr in orgnames if pr != p and p in pr] 
		if len(check) > 0: 
			if debug:
				if len(check) == 1:
					print "\n))))Found possible LOCATION subsummed by ORGANIZATION! location p: "+p+" is subsummed by personr: "+check[0]
					if p in check[0]:  #p subsummed by check[0] so copy p's ID and sentence into check[0]s
						for i in dis_entities["LOCATION"][p]['id']:
							if i not in dis_entities["ORGANIZATION"][check[0]]['id']:
								dis_entities["ORGANIZATION"][check[0]]['id'].append(i)					
						dis_entities["ORGANIZATION"][check[0]]['id'].sort()					

						for i in dis_entities["LOCATION"][p]['sentence']:
							if i not in dis_entities["ORGANIZATION"][check[0]]['sentence']:
								dis_entities["ORGANIZATION"][check[0]]['sentence'].append(i)					
						dis_entities["ORGANIZATION"][check[0]]['sentence'].sort()					

						del dis_entities["LOCATION"][p]
						#TODO DO I NEED TO REMOVE THE DELETE ONE FROM GLOBAL anything global_index perhaps????
				else:
					print "\n!))))Found possible LOCATION subsummed by various ORGANIZATIONS! LOC p: "+p+" is subsummed by pr: "+str(check)
					#TODO HOW TO MERGE THESE , look to see if this occurs !)))))


	if debug:
		printflush("After Filter Entities, dis_entities")
		for d in dis_entities:
			printflush(d)
			for de in dis_entities[d]:
				printflush("\t"+de+" : "+ str(dis_entities[d][de]))
		
        	filter_end = time.clock()
		printflush("TIME INFORMATION:  FILTERING TOOK "+str((filter_end - filter_start))+" seconds")

	return dis_entities

    
@timeout(100)  #timeout after 100 seconds
def verify_and_save_relations(queryobj,entrelations,dis_entities,sentences,art,add_extra_links,db,debug):
    sentnums, bgrelations = entrelations
    global global_relations
    global_entity_index, global_entity_obj = get_global_entity_by_name(queryobj[1])
     
    centerobj = [queryobj[1], global_entity_index]
    #url = art['_source']['url']
    url = art['url']
    
    if len(sentnums) > 1:
        #THIS IS SO IT WORKS FOR MULTIPLE MATCHES OF POLITICIAN
        if debug:
            printflush("MULTIPLE DIRECT HITS: ")
            #use these two lines to only use first hit
            #sentnums = [sentnums[0]]
            #relations = relations[0]
            printflush("\nSent nums" + str(sentnums))
            printflush("\nbgrelations")
            for bg in bgrelations:
                printflush("\n")
                printflush(bg)
            printflush("\nDISAMBIGUATED ENTITIES:")
            printflush(dis_entities)               
    else:    
        same_sent, prior_sents, next_sents, prior_far_sents, next_far_sents = bgrelations
        if debug:
            printflush("POLITICIAN: "+ queryobj[1]+"\nALL SENTENCES")
            printflush(sentences)
            printflush("\nSAME SENTENCE: ")
            printflush(same_sent)
            printflush("\nNEAR SENTENCES:")
            printflush(prior_sents)
            printflush(next_sents)
            printflush("\nFAR SENTENCES:")
            printflush(prior_far_sents)
            printflush(next_far_sents)
            printflush("\nDISAMBIGUATED ENTITIES:")
            printflush(dis_entities)               
            #print "POLITICIAN INFO (at index "+str(global_entity_index)+" ):"
            #print global_entity_obj
            
    #to avoid output of get_ent_to_glo
    pred = debug
    if len(sentnums) > 1:
        debug = False
        
    ent_to_global,ent = get_ent_to_global(dis_entities,debug) 
    debug = pred
    
    #get local index of politician along with global index and global object
    loc_index = get_local_index(queryobj,ent,debug)                    
    global_index_val = global_index[loc_index]   #loc_index is the word which is the key in the global index
    global_obj = global_entities[global_index_val]
    
    if debug:
        printflush("index of politician in local entity list: "+loc_index)
        printflush("index of politician in global entity list: "+str(global_index_val))
        #print global_obj
    
    
    #Now Create Relations with ent_to_global, etc
    
    if debug:
        printflush("\nNow add relationships from Same Sentence:")
    relations = []
    if len(sentnums) == 1:
        sentn = sentnums[0]
        relations = handle_single_match_same_sentence(sentn, relations, ent_to_global,same_sent,global_index_val, loc_index, sentences,debug)                    
    else:
        if debug:
            printflush("handle more than one direct sentence match")  #TODO HANDLE MULTIPLE SIMILARLY
        for i,sentn in enumerate(sentnums):
            same_sent, prior_sents, next_sents, prior_far_sents, next_far_sents = bgrelations[i]  
            if debug:
                printflush("\t sentnum: "+str(sentn))
                printflush("\t with same sent!")
                printflush(same_sent)
            relations = handle_single_match_same_sentence(sentn, relations, ent_to_global,same_sent,global_index_val, loc_index, sentences, debug)                    
            
            
            
    if debug:
        printflush("After Same Sentence, Relations:")
        printflush(relations)
        printflush("\nNow add relationships from Prior Sentences:")
        
    if len(sentnums) == 1:
        subtype = "prior"
        relations = handle_single_match_near_sentences(sentn,subtype,ent_to_global, prior_sents, global_index_val, loc_index, relations, sentences, debug)             
    else:
        #HANDLE MULTIPLE HITS NEAR PRIOR
        if debug:
            printflush("More than one direct sentence match"  )
        relations, bgrelations = handle_multiple_match_near_sentences(sentnums,bgrelations,ent_to_global,global_index_val,loc_index,relations,sentences, debug)
                            
                         
    if debug:
        printflush("After Prior Sentence, Relations is :" )
        printflush(relations)
        printflush("\nNow add relationships from Next Sentences:"  )
        
    if len(sentnums) == 1:
        subtype = "post"
        relations = handle_single_match_near_sentences(sentn,subtype,ent_to_global, next_sents, global_index_val, loc_index, relations, sentences, debug)
    else:        
        #HANDLE MULTIPLE HITS NEAR NEXT
        if debug:
            printflush("handle more than one next sentence match")
        subtype = "post"
        for i,sentn in enumerate(sentnums):
            same_sent, prior_sents, next_sents, prior_far_sents, next_far_sents = bgrelations[i]  
            if debug:
                printflush("\t sentnum: "+str(sentn))
                printflush("\t with next sents!")
                printflush(next_sents)
            relations = handle_single_match_near_sentences(sentn,subtype,ent_to_global, next_sents, global_index_val, loc_index, relations, sentences, debug)
       
              
    if debug:
        printflush("\nNow add relationships from Rest of Sentences:")
           
    if len(sentnums) == 1:
        rest = prior_far_sents + next_far_sents
        relations = handle_single_match_far_sentences(ent_to_global, rest, global_index_val, loc_index, relations, debug)                                                   
    else:
        #HANDLE MULTIPLE HITS FAR
        if debug:
            printflush("handle article level matches which weren't priorly added as near or same sentence")
        relations, bgrelations = handle_multiple_match_far_sentences(sentnums,bgrelations,sentences,ent_to_global,global_index_val,loc_index,relations,dis_entities,debug)
                         
                          
    if debug:    
        print "\nMADE THE FOLLOWING RELATIONS ("+str(len(relations))+"):"
        for i,rel in enumerate(relations):            
            printflush(rel)
    
    marked_as_slow = False
    #if len(relations) > 0:   #instead of 80, so just disallow far relations
    #if debug:
    #printflush("\nFound "+str(len(relations))+" relations for article with "+str(len(sentences))+" sentences and URL: "+url+" before adding extras, so its likely that this is a list of things and that we shouldn't take far far extra relationshipts into account")

    #marked_as_slow = True    #IS THIS CORRECT?  <-- if it goes to slow, uncomment this out
        
    if add_extra_links == True:
	#debug = True
        if debug:
            printflush("\n<<<<<<<<ADD EXTRA LINKS (ie, non main politician based)")
            printflush("Direct Hits: " + str(sentnums))
                    
        #NOW HANDLE MAKING LINKS BETWEEN ALL EXCEPT THE ORIGINAL POLITICIAN
        if len(sentnums) == 1:   
            sentn = sentnums[0]
            #relations = handle_single_add_extra_links(sentn,relations,ent_to_global,dis_entities,sentences, marked_as_slow, debug)                
            relations = handle_single_add_extra_linkstwo(sentn,relations,ent_to_global,dis_entities,sentences, marked_as_slow, centerobj, debug)                
        else:
            if debug:
                printflush("Handle Add Extra for Multiple Case:")
                
            for i,sentn in enumerate(sentnums):
                if debug:
                    printflush("*^*^*^*^*CALL with "+str(sentn))
                #relations = handle_single_add_extra_links(sentn,relations,ent_to_global,dis_entities,sentences, marked_as_slow, debug)                
                relations = handle_single_add_extra_linkstwo(sentn,relations,ent_to_global,dis_entities,sentences, marked_as_slow, centerobj, debug)                
	#debug = False
    
        if debug:
		print "\nAFTER MADE THE FOLLOWING RELATIONS ("+str(len(relations))+"):"
        #for i,rel in enumerate(relations):            
        #    printflush(rel)
	#sys.exit()

    moid = str(art['_id'])
    moid = moid.replace("ObjectId(","").replace(")",'')   #NEW
    res = {'url':url, 'entities': ent, 'relations': relations, 'date': art['date'], 'mongoid':moid, 'num_sentences':len(sentences)}
    global_relations[url] = res

    return res



@timeout(30)  #timeout after thirty seconds
def verify_and_save_large_relations(currentname,entrelations,dis_entities,sentences,art,add_extra_links,db,debug):
    if debug:
	printflush("XXXX IN VERIFY LARGE RELATIONS\n")
    sentnums, bgrelations = entrelations
    global global_relations
    global_entity_index, global_entity_obj = get_global_entity_by_name(currentname)
    url = art['url']
    
    if len(sentnums) > 1:
        #THIS IS SO IT WORKS FOR MULTIPLE MATCHES OF POLITICIAN
        if debug:
            printflush("MULTIPLE DIRECT HITS: ")
            #use these two lines to only use first hit
            #sentnums = [sentnums[0]]
            #relations = relations[0]
            printflush("\nSent nums" + str(sentnums))
            printflush("\nbgrelations")
            for bg in bgrelations:
                printflush("\n")
                printflush(bg)
    else:    
        same_sent, prior_sents, next_sents, prior_far_sents, next_far_sents = bgrelations
        if debug:
            printflush("ENTITY: "+ currentname+"\nALL SENTENCES")
            printflush(sentences)
            printflush("\nSAME SENTENCE: ")
            printflush(same_sent)
            printflush("\nNEAR SENTENCES:")
            printflush(prior_sents)
            printflush(next_sents)
            printflush("\nFAR SENTENCES:")
            printflush(prior_far_sents)
            printflush(next_far_sents)
            printflush("\nDISAMBIGUATED ENTITIES:")
            printflush(dis_entities)               
            #print "POLITICIAN INFO (at index "+str(global_entity_index)+" ):"
            #print global_entity_obj
            
    #to avoid output of get_ent_to_glo
    pred = debug
    if len(sentnums) > 1:
        debug = False
        
    ent_to_global,ent = get_ent_to_global(dis_entities,debug) 
    debug = pred
    
    #get local index of politician along with global index and global object
    loc_index = get_local_index(["",currentname],ent,debug)                    
    global_index_val = global_index[loc_index]   #loc_index is the word which is the key in the global index
    global_obj = global_entities[global_index_val]
    
    if debug:
        printflush("index of politician in local entity list: "+loc_index)
        printflush("index of politician in global entity list: "+str(global_index_val))
        #print global_obj
    
    
    #Now Create Relations with ent_to_global, etc
    
    if debug:
        printflush("\nNow add relationships from Same Sentence:")
    relations = []
    if len(sentnums) == 1:
        sentn = sentnums[0]
        relations = handle_single_match_same_sentence(sentn, relations, ent_to_global,same_sent,global_index_val, loc_index, sentences,debug)                    
    else:
        if debug:
            printflush("handle more than one direct sentence match")  #TODO HANDLE MULTIPLE SIMILARLY
        for i,sentn in enumerate(sentnums):
            same_sent, prior_sents, next_sents, prior_far_sents, next_far_sents = bgrelations[i]  
            if debug:
                printflush("\t sentnum: "+str(sentn))
                printflush("\t with same sent!")
                printflush(same_sent)
            relations = handle_single_match_same_sentence(sentn, relations, ent_to_global,same_sent,global_index_val, loc_index, sentences, debug)                    
            
            
            
    if debug:
        printflush("After Same Sentence, Relations:")
        printflush(relations)
        printflush("\nNow add relationships from Prior Sentences:")
        
    if len(sentnums) == 1:
        subtype = "prior"
        relations = handle_single_match_near_sentences(sentn,subtype,ent_to_global, prior_sents, global_index_val, loc_index, relations, sentences, debug)             
    else:
        #HANDLE MULTIPLE HITS NEAR PRIOR
        if debug:
            printflush("More than one direct sentence match"  )
        relations, bgrelations = handle_multiple_match_near_sentences(sentnums,bgrelations,ent_to_global,global_index_val,loc_index,relations,sentences, debug)
                            
                         
    if debug:
        printflush("After Prior Sentence, Relations is :" )
        printflush(relations)
        printflush("\nNow add relationships from Next Sentences:"  )
        
    if len(sentnums) == 1:
        subtype = "post"
        relations = handle_single_match_near_sentences(sentn,subtype,ent_to_global, next_sents, global_index_val, loc_index, relations, sentences, debug)
    else:        
        #HANDLE MULTIPLE HITS NEAR NEXT
        if debug:
            printflush("handle more than one next sentence match")
        subtype = "post"
        for i,sentn in enumerate(sentnums):
            same_sent, prior_sents, next_sents, prior_far_sents, next_far_sents = bgrelations[i]  
            if debug:
                printflush("\t sentnum: "+str(sentn))
                printflush("\t with next sents!")
                printflush(next_sents)
            relations = handle_single_match_near_sentences(sentn,subtype,ent_to_global, next_sents, global_index_val, loc_index, relations, sentences, debug)
       
              
    if debug:
        printflush("\nNow add relationships from Rest of Sentences:")
           
    if len(sentnums) == 1:
        rest = prior_far_sents + next_far_sents
        relations = handle_single_match_far_sentences(ent_to_global, rest, global_index_val, loc_index, relations, debug)                                                   
    else:
        #HANDLE MULTIPLE HITS FAR
        if debug:
            printflush("handle article level matches which weren't priorly added as near or same sentence")
        relations, bgrelations = handle_multiple_match_far_sentences(sentnums,bgrelations,sentences,ent_to_global,global_index_val,loc_index,relations,dis_entities,debug)
                         
                          
    if debug:    
        print "\nMADE THE FOLLOWING RELATIONS "+str(len(relations))+":"
        for i,rel in enumerate(relations):            
            printflush(rel)
    
    #if add_extra_links == False:
    #    printflush("\nFound "+str(len(relations))+" relations for URL: "+url+" without adding extras")
    #else:
    
    marked_as_slow = False
    if len(relations) > 0:   #instead of 80, so just disallow far relations
        if debug:
            printflush("\nFound "+str(len(relations))+" relations for URL: "+url+" before adding extras, so its likely that this is a list of things and that we shouldn't take far far extra relationshipts into account")
        marked_as_slow = True
        
    if add_extra_links == True:
        if debug:
            printflush("\n<<<<<<<<ADD EXTRA LINKS (ie, non main politician based)")
            printflush("Direct Hits: " + str(sentnums))
                    
        #NOW HANDLE MAKING LINKS BETWEEN ALL EXCEPT THE ORIGINAL POLITICIAN
        if len(sentnums) == 1:   
            sentn = sentnums[0]
            relations = handle_single_add_extra_links(sentn,relations,ent_to_global,dis_entities,sentences, marked_as_slow, debug)                
        else:
            if debug:
                printflush("Handle Add Extra for Multiple Case:")
                
            for i,sentn in enumerate(sentnums):
                if debug:
                    printflush("*^*^*^*^*CALL with "+str(sentn))
                relations = handle_single_add_extra_links(sentn,relations,ent_to_global,dis_entities,sentences, marked_as_slow, debug)                

    if debug:
	print("\nZZZZZ AFTER ALL VERIFY relations=")
	print("\nFound "+str(len(relations))+" relations for URL: "+url+" after adding extras, so its likely that this is a list of things and that we shouldn't take far far extra relationshipts into account")
	print relations


    moid = str(art['_id'])
    moid = moid.replace("ObjectId(","").replace(")",'')   #NEW
    res = {'url':url, 'entities': ent, 'relations': relations, 'date': art['date'], 'mongoid':moid, 'num_sentences':len(sentences)}
    
    #DON'T SAVE TO GLOBAL RELATIONS
    #global_relations[url] = res
    return res



def add_text_snippet(text):
    #give edge (source1-source2-exacthit) that contains snippet an index in text_snippets and return id 
    text_snippets.append(text)
    return len(text_snippets) - 1


def update_entity_counter_small(source,target,debug=False):
    global entity_edges
    if debug: printflush("In Update Entity Counter Small")
    if source not in entity_edges:
        entity_edges[source] = {'counter':1,'edges':[{target:1}]}
    else:
        entity_edges[source]['counter'] = entity_edges[source]['counter'] + 1
        f = 0
        if debug: printflush("In Update Entity Source looking for "+str(target))
        for i,ed in enumerate(entity_edges[source]['edges']):                       
            #if debug: printflush(ed)
                
            if ed.keys()[0] == target:  
                f = 1
                if debug: printflush("Found "+str(target)+" so update counter!")
                #entity_edges[source]['edges'][target] = entity_edges[source]['edges'][target] + 1
                ed[ed.keys()[0]] = ed[ed.keys()[0]] + 1
                break
        if f == 0:
            if debug: printflush("Didn't find "+str(target)+" so add it")
            entity_edges[source]['edges'].append({target:1})

    if target not in entity_edges:
        entity_edges[target] = {'counter':1,'edges':[{source:1}]}
    else:
        entity_edges[target]['counter'] = entity_edges[target]['counter'] + 1
        f = 0
        for i,ed in enumerate(entity_edges[target]['edges']):
            if ed.keys()[0] == source:
                f = 1
                #entity_edges[target]['edges'][source] = entity_edges[target]['edges'][source] + 1
                ed[ed.keys()[0]] = ed[ed.keys()[0]] + 1
                break
        if f == 0:
            entity_edges[target]['edges'].append({source:1})


def update_entity_counter(source,target,edge_lookup,debug=False):
    #am i double counting edges?  hmm..  just based on adding it for both source-target, and target-source ( since its undirected )
    global entity_edges

    if source not in entity_edges:
        entity_edges[source] = {'counter':1,'edges':[{target:1}]}
    else:
        entity_edges[source]['counter'] = entity_edges[source]['counter'] + 1
        f = 0

        #if debug: printflush("In Update Entity Source with source("+str(source)+") looking for target "+str(target)+" in edges array of size: "+str(len(entity_edges[source]['edges']))+"\n")

	try:
		if source in edge_lookup and target in edge_lookup[source]:
			entity_edges[source]['edges'][edge_lookup[source][target]] += 1
			f = 1
	except:  
		for i,ed in enumerate(entity_edges[source]['edges']):               #pass in look up will make this faster!!  TODO 
		    if ed.keys()[0] == target:  
			f = 1
			ed[ed.keys()[0]] = ed[ed.keys()[0]] + 1
			break

        if f == 0:
            #if debug: printflush("\tDidn't find "+str(target)+" so add it")
            entity_edges[source]['edges'].append({target:1})


    if target not in entity_edges:
        entity_edges[target] = {'counter':1,'edges':[{source:1}]}
    else:
	try:
		if target in edge_lookup and source in edge_lookup[target]:
			entity_edges[target]['edges'][edge_lookup[target][source]] += 1
			f = 1
	except:
		entity_edges[target]['counter'] = entity_edges[target]['counter'] + 1
		f = 0
		for i,ed in enumerate(entity_edges[target]['edges']):
		    if ed.keys()[0] == source:
			f = 1
			#entity_edges[target]['edges'][source] = entity_edges[target]['edges'][source] + 1
			ed[ed.keys()[0]] = ed[ed.keys()[0]] + 1
			break
	
        if f == 0:
            entity_edges[target]['edges'].append({source:1})


def add_intermediate_json_relations_small(global_rels,debug=False):
    global global_entities
    global edges_seen
    global json_output
    global entity_edges

    if debug:
        printflush("In ADD SMALL INTERMEDIATE Json Relations with number of relations: "+str(len(global_rels['relations'])))
	printflush("JSON OUTPUT EDGES ("+str(len(json_output["elements"]["edges"]))+" ) and NODES ("+str(len(json_output["elements"]["nodes"]))+")")
        v_start = time.clock()
        
    new_edges = {'edges':[]}
    added_inst_to = {'edges':[]}
    
    #make one prelook up table for where edges are located in jsonoutput so you don't have to loop through it for every person!!
    jso_lookup = {}
    nothing = 0
    for n,edg in enumerate(json_output["elements"]["edges"]):    
	eds = edg['data']['source']
	edt = edg['data']['target']
	if eds in jso_lookup:
		if edt not in jso_lookup:
			jso_lookup[eds][edt] = n
		else:
			nothing = nothing + 1
	else:
		jso_lookup[eds] = {edt:n}
	
    if debug: 
	printflush("NOTHING with count: "+str(nothing)+" and jso_lookup ")
     	j_lkup = time.clock()
	printflush("\nTIME INFORMATION:  construct jso_lookup took "+str(j_lkup - r_copy)+" seconds ")


    for i,gr in enumerate(global_rels):
        for r in gr['relations']:
            inst = {}
            inst['source'] = r['term1_id']
            inst['target'] = r['term2_id']
            
            ei = {}
            ei['type'] = r['type']
	    grmid = str(gr['mongoid']).replace("ObjectId(","").replace(")",'')   #NEW
            ei['mongoid'] = grmid

	    #IMPORTANT DON'T PREFILTER OUT SAME ARTICLE ONES !
	    if 'text_snippet' not in r:
		if ei['type'] != 'same article':
			if debug:
				printflush("ERROR didn't find text_snippet in r")
				printflush(r)
				printflush(ei)
	    else:
		textid = add_text_snippet(r['text_snippet'])
		ei['textid'] = textid
            

            inst['inst'] = [ei]
            
            #check if it exits, either source-target or target-source   #I CAN MAKE THIS FASTER (make a dictionary look up by source or target!
	    f = 0
	    if inst['source'] in entity_edges:
		#if debug: printflush("Looking through "+str(len(entity_edges[inst['source']]['edges']))+" edges of source: "+str(inst['source'])+" for target: "+str(inst['target'])
		for i,ed in enumerate(entity_edges[inst['source']]['edges']):                       
		    if ed.keys()[0] == inst['target']:  
			f = 1
			s = inst['source']
			t = inst['target']
			break
	    elif inst['target'] in entity_edges:
		#if debug: printflush("Looking through "+str(len(entity_edges[inst['target']]['edges']))+" edges of target: "+str(inst['target'])+" for source: "+str(inst['source'])
		for i,ed in enumerate(entity_edges[inst['target']]['edges']):                       
		    if ed.keys()[0] == inst['source']:  
			f = 1
			s = inst['target']
			t = inst['source']
			break
	    
	    if f == 1:
		if debug:  printflush("NOW LOOKING INTO JSO_LOOKUP WITH source: "+str(s)+" and target: "+str(t))
		if s in jso_lookup:
			if t in jso_lookup[s]:
				if debug: printflush("Found source: "+str(s)+" and target: "+str(t) +" in jso_lookup and it says its edge: "+str(jso_lookup[s][t]))
				try:
					edg = json_output["elements"]["edges"][jso_lookup[s][t]]
					edg['data']['inst'].append(ei)
					if debug: printflush(ei)
					added_inst_to['edges'].append({"data":inst})
					update_entity_counter_small(s,t,debug)

					f = 2
				except:
					traceback.print_exc(file=sys.stdout)
					printflush("EXCEPTION IN jso_lookup.. so try to find where edge is actually")
                			for xx,edg in enumerate(json_output["elements"]["edges"]):        
                				if edg['data']['source'] == s and edg['data']['target'] == t:
							printflush("FOUND EDGE AT INDEX "+str(xx)+" whereas the lookup table says its at "+str(jso_lookup[s][t]))
							break
					sys.exit()
		if f == 1:
			
			if debug:
				printflush("f==1 so didn't find val in lookup table: s= "+str(s)+" AND t= "+str(t)+"...")
				printflush("s in jso_lookup: "+str(s in jso_lookup))
			if s in jso_lookup:
				if debug: printflush("t in jso_lookup[s]: "+str(t in jso_lookup[s]))
				if t in jso_lookup[t]:
					printflush("\nKKKK THIS SHOULD HAVE WORKED SO LOOK INTO IT")
				else:
					if debug:
						printflush("HERE SOURCE s "+str(s)+", IS IN JSO_LOOKUP BUT TARGET t "+str(t)+", ISN't IN JSO_LOOKUP[SOURCE] EVEN THOUGH IT IS IN ENTITY_EDGES")
						printflush("\nSO EITHER entity_edges is incorrect (unlikely) or I need to update lookup table and then add edge")
					#print jso_lookup[s]
					json_output["elements"]["edges"].append({"data":inst})  
					jso_lookup[s][t] = len(json_output["elements"]["edges"]) - 1  
					new_edges['edges'].append({"data":inst})                    
					update_entity_counter_small(s,t,debug)

			else:
				#didn't find in look up table but add anyways ( why wasn't it found )
				json_output["elements"]["edges"].append({"data":inst})  
				#add to jso_lookup!  
				if inst['source'] in jso_lookup:
					if inst['target'] in jso_lookup[inst['source']]:
						printflush("REALLY SHOULDNT HAVE GOTTEN HERE")
						reallyshouldnthavegottenhere = 1
					else:
						jso_lookup[inst['source']][inst['target']] = len(json_output["elements"]["edges"]) - 1			
				else:
						jso_lookup[inst['source']] = {inst['target']: len(json_output["elements"]["edges"]) - 1 } 			

				new_edges['edges'].append({"data":inst})                    
				update_entity_counter_small(inst['source'],inst['target'],debug)

            else:
	    	json_output["elements"]["edges"].append({"data":inst})  
		#add to jso_lookup!  
		if inst['source'] in jso_lookup:
			if inst['target'] in jso_lookup[inst['source']]:
				reallyshouldnthavegottenhere = 1
			else:
				jso_lookup[inst['source']][inst['target']] = len(json_output["elements"]["edges"]) - 1			
		else:
				jso_lookup[inst['source']] = {inst['target']: len(json_output["elements"]["edges"]) - 1 } 			

	    	new_edges['edges'].append({"data":inst})                    
	    	update_entity_counter_small(inst['source'],inst['target'],debug)

        
def add_intermediate_json_relations(res,num_instances,debug=False):
    #THIS FUNCTION SPLITS BETWEEN SMALL VERSION WHICH WORKS QUICKLY FOR MOST CASES AND BIG ONE WHICH IS OPTIMIZED FOR BIG RESULT SETS
        
    global_rels = [res.copy()]        #this is just the relations for the current article ( and not cumulative from priors )    

    num_entities =  len(res['entities'])
    num_sents = res['num_sentences']
    prod = num_instances * num_entities * num_sents
	
    prodthreshold = 8000  #for Gene Green with this cutoff it took 951, for Abel Herrero with this cuttoff its 436
    #prodthreshold = 6000   #for GG with this cutoff it takes 1020, for Abel Herrrero with this cutoff its 429 

    if prod > prodthreshold:   #maybe change this to be lower
	#do big way
    	printflush("\t\t**IN ADD INTERMEDIATE JSON WITH insts: "+str(num_instances)+", ents: "+str(num_entities)+", sents: "+str(num_sents)+", and prod: "+str(prod)+ " ... CALL BIG")
        add_intermediate_json_relations_big(global_rels,debug)
    else:
    	printflush("\t\t**IN ADD INTERMEDIATE JSON WITH insts: "+str(num_instances)+", ents: "+str(num_entities)+", sents: "+str(num_sents)+", and prod: "+str(prod)+ " ... CALL SMALL")
        add_intermediate_json_relations_small(global_rels,debug)



def add_intermediate_json_relations_big(global_rels,debug=False):
    global json_output
    global entity_edges

    if debug:
        printflush("In ADD BIG INTERMEDIATE Json Relations with number of relations: "+str(len(global_rels['relations'])))
	printflush("JSON OUTPUT EDGES ("+str(len(json_output["elements"]["edges"]))+" ) and NODES ("+str(len(json_output["elements"]["nodes"]))+")")
        v_start = time.clock()
     	r_copy = time.clock()

    #make one prelook up table for where edges are located in jsonoutput so you don't have to loop through it for every person!!
    jso_lookup = {}
    nothing = 0
    for n,edg in enumerate(json_output["elements"]["edges"]):    
	eds = edg['data']['source']
	edt = edg['data']['target']
	if eds in jso_lookup:
		if edt not in jso_lookup:
			jso_lookup[eds][edt] = n
		else:
			nothing = nothing + 1
	else:
		jso_lookup[eds] = {edt:n}
	
    if debug: 
	print "NOTHING with count: "+str(nothing)+" and jso_lookup"
     	j_lkup = time.clock()
	print "\nTIME INFORMATION:  construct jso_lookup took "+str(j_lkup - r_copy)+" seconds "
	#print jso_lookup

    #possibly also make prelookup for main entity person ( so you don't have to go through their edges ).. but only if this is saves time
    #this one is only ever called for small network purposes ( the other one for large networks is in generate_networks ) so do this
    source_lookup = {}
    edge_lookup = {}
    for i,e in enumerate(entity_edges):
	edge_lookup[e] = {k: n for n,ed in enumerate(entity_edges[e]['edges']) for k,v in ed.iteritems() }
	source_lookup[e] = set([k for ed in entity_edges[e]['edges'] for k,v in ed.iteritems()])

    if debug:
	print "Source Lookup"
	#print source_lookup
	'''
	Entity_Edges
{417: {'counter': 1, 'edges': [{123: 1}]}, 419: {'counter': 1, 'edges': [{123: 1}]}, 389: {'counter': 1, 'edges': [{123: 1}]}, 422: {'counter': 1, 'edges': [{123: 1}]}, 383: {'counter': 1, 'edges': [{123: 1}]}, 247: {'counter': 1, 'edges': [{123: 1}]}, 186: {'counter': 1, 'edges': [{123: 1}]}, 123: {'counter': 10, 'edges': [{389: 1}, {383: 1}, {127: 2}, {247: 1}, {419: 1}, {417: 1}, {422: 1}, {186: 1}, {134: 1}]}, 134: {'counter': 1, 'edges': [{123: 1}]}, 127: {'counter': 2, 'edges': [{123: 2}]}}
	'''
	print "Entity_Edges"
	#print entity_edges


    for i,gr in enumerate(global_rels):   
	#TODO DIDNT find is being called.. SOURCE should be in source_lookup at this point if its in entity_edges correct?   FIGURE THIS OUT.. once it works add all changes to generate (including ones you made to update counters!) 

        for r in gr['relations']:
            inst = {'source':r['term1_id'],'target':r['term2_id']}

	    grmid = str(gr['mongoid']).replace("ObjectId(","").replace(")",'') #can i not do this somehow
            ei = {'type':r['type'],'mongoid':grmid}
            ei['mongoid'] = grmid
	    if 'text_snippet' in r:
		textid = add_text_snippet(r['text_snippet'])
		ei['textid'] = textid
            

            inst['inst'] = [ei]
            
	    f = 0
	    if inst['source'] in entity_edges:
		if inst['source'] in source_lookup:
		    if inst['target'] in source_lookup[inst['source']]:  
			if debug: print "FOUND TARGET IN SOURCE_LOOKUP"
			f = 1
			s = inst['source']
			t = inst['target']
		else:
			#if debug == debug: print "DIDNT FIND inst[source] = "+str(inst['source'])+" in source_lookup"  #pretty sure this isn't being used so don't worry about it, but check
			for i,ed in enumerate(entity_edges[inst['source']]['edges']):                       
			    if ed.keys()[0] == inst['target']:  
				f = 1
				s = inst['source']
				t = inst['target']
				break

	    elif inst['target'] in entity_edges:
		if inst['target'] in source_lookup:
		    if inst['source'] in source_lookup[inst['target']]:  
			if debug == debug: print "FOUND SOURCE IN TARGET_LOOKUP <-- definitely not expecting this"
			f = 1
			s = inst['target']
			t = inst['source']
		else:
			if debug == debug: print "DIDNT FIND inst[target] = "+str(inst['target'])+" in target_lookup"  #if either this or the above occurs make it faster with sets!
			for i,ed in enumerate(entity_edges[inst['target']]['edges']):                       
			    if ed.keys()[0] == inst['source']:  
				f = 1
				s = inst['target']
				t = inst['source']
				break


	    if f == 1:
                #add to existing edge 
		if debug:  print "\nNOW LOOKING INTO JSO_LOOKUP WITH source: "+str(s)+" and target: "+str(t)

		if s in jso_lookup:
			if t in jso_lookup[s]:
				if debug: print "\tFound source: "+str(s)+" and target: "+str(t) +" in jso_lookup and it says its edge: "+str(jso_lookup[s][t])
				try:
					edg = json_output["elements"]["edges"][jso_lookup[s][t]]
					edg['data']['inst'].append(ei)
					update_entity_counter(s,t,edge_lookup,debug)

					if s in source_lookup:
						if t not in source_lookup[s]:
							if debug: print "UPDATE SOURCE LOOKUP COUNTER1: for source: "+str(s)+" found no target: "+str(t) +" in source_lookup so add it"
							source_lookup[s].add(t) 
					else:
						if debug: print "UPDATE SOURCE LOOKUP COUNTER3: source not found "+str(s)+" and found no target: "+str(t) +" in source_lookup so add it"
						source_lookup[s] = set([t])
					
					f = 2
				except:
					traceback.print_exc(file=sys.stdout)
					print "\n***EXCEPTION IN jso_lookup.. so try to find where edge is actually"
                			for xx,edg in enumerate(json_output["elements"]["edges"]):        
                				if edg['data']['source'] == s and edg['data']['target'] == t:
							print "FOUND EDGE AT INDEX "+str(xx)+" whereas the lookup table says its at "+str(jso_lookup[s][t])
							break
					sys.exit()
		if f == 1:
			if debug:
				print "f==1 so didn't find val in lookup table: s= "+str(s)+" AND t= "+str(t)+"..."
				print "s in jso_lookup: "+str(s in jso_lookup)
			if s in jso_lookup:
				if debug: print "t in jso_lookup[s]: "+str(t in jso_lookup[s])
				if t in jso_lookup[t]:
					print "\nKKKK THIS SHOULD HAVE WORKED SO LOOK INTO IT"
				else:
					if debug:
						print "HERE SOURCE s "+str(s)+", IS IN JSO_LOOKUP BUT TARGET t "+str(t)+", ISN't IN JSO_LOOKUP[SOURCE] EVEN THOUGH IT IS IN ENTITY_EDGES"
						print "\nSO EITHER entity_edges is incorrect (unlikely) or I need to update lookup table and then add edge"
						#print jso_lookup[s]
					json_output["elements"]["edges"].append({"data":inst})  
					jso_lookup[s][t] = len(json_output["elements"]["edges"]) - 1  
					update_entity_counter(s,t,edge_lookup,debug)

					if s in source_lookup:
						if t not in source_lookup[s]:
							if debug: print "UPDATE SOURCE LOOKUP COUNTER4: for source: "+str(s)+" found no target: "+str(t) +" in source_lookup so add it"
							source_lookup[s].add(t) 
					else:
						if debug: print "UPDATE SOURCE LOOKUP COUNTER6: source not found "+str(s)+" and found no target: "+str(t) +" in source_lookup so add it"
						source_lookup[s] = set([t])
			else:
				#didn't find in look up table but add anyways ( why wasn't it found )
				json_output["elements"]["edges"].append({"data":inst})  
				#add to jso_lookup!  
				if inst['source'] in jso_lookup:
					if inst['target'] in jso_lookup[inst['source']]:
						reallyshouldnthavegottenhere = 1
					else:
						jso_lookup[inst['source']][inst['target']] = len(json_output["elements"]["edges"]) - 1			
				else:
						jso_lookup[inst['source']] = {inst['target']: len(json_output["elements"]["edges"]) - 1 } 			

				update_entity_counter(inst['source'],inst['target'],edge_lookup,debug)

				if s in source_lookup:
					if t not in source_lookup[s]:
						if debug: print "UPDATE SOURCE LOOKUP COUNTER7: for source: "+str(s)+" found no target: "+str(t) +" in source_lookup so add it"
						source_lookup[s].add(t) 
				else:
					if debug: print "UPDATE SOURCE LOOKUP COUNTER9: source not found "+str(s)+" and found no target: "+str(t) +" in source_lookup so add it"
					source_lookup[s] = set([t])
                
            else:
	    	json_output["elements"]["edges"].append({"data":inst})  
		#add to jso_lookup!  
		if inst['source'] in jso_lookup:
			if inst['target'] in jso_lookup[inst['source']]:
				reallyshouldnthavegottenhere = 1
			else:
				jso_lookup[inst['source']][inst['target']] = len(json_output["elements"]["edges"]) - 1			
		else:
				jso_lookup[inst['source']] = {inst['target']: len(json_output["elements"]["edges"]) - 1 } 			

	    	update_entity_counter(inst['source'],inst['target'],edge_lookup, debug)

		s = inst['source']
		t = inst['target']
		if s in source_lookup:
			if t not in source_lookup[s]:
				if debug: print "UPDATE SOURCE LOOKUP COUNTER10: for source: "+str(s)+" found no target: "+str(t) +" in source_lookup so add it"
				source_lookup[s].add(t) 
		else:
			if debug: print "UPDATE SOURCE LOOKUP COUNTER12: source not found "+str(s)+" and found no target: "+str(t) +" in source_lookup so add it"
			source_lookup[s] = set([t])

