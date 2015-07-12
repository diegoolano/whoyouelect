from dama_globals import *
from dama_utils import *   #for db
import time
import json
import sys
try:
	import cPickle as pickle
except:
	import pickle
import copy
import tarfile
import os.path
import os
from shutil import copyfile, move
import traceback
from wiki_funcs import *
from go_through_small_medium_config_jsons_and_add_wikiurl_and_photorul_to_mongo import *

#from verify_and_save_relations import *

#GARNET COLEMAN IS NOW A VARIABLE FOR WHOEVER THE CENTRAL FIGURE IS
basep = "/Users/dolano/htdocs/dama-larca/d3/"    #BASE PATH 
datap = basep + "generate_network/"
saved_jsons_path = datap + "data/jsons"
htmlpath = basep + "whoyouelect/whoyouelect.com/texas/data/"
save_config_file = basep + "/whoyouelect/whoyouelect.com/texas/js/config.json"
save_configdesc_file = basep + "/whoyouelect/whoyouelect.com/texas/js/configdesc.json"

def generate_url_list():
    #http://www.whoyouelect.com/data/smallnet-urls-march17.json
    #needs to be indexed by a numeric value  ( 1 - ... ) and not a mongoid
    #printflush("ZZZZ CALL TO GENERATE_URL_LIST")
    global global_relations
    #make url list indexed by mongoid so that edges just need mongoid to show id
    url_list = {}
    for i,gr in enumerate(global_relations):
        mongoid = global_relations[gr]['mongoid']
	mongoid = mongoid.replace("ObjectId(","").replace(")",'')
        url_list[mongoid] = {'url':global_relations[gr]['url'], 'date': global_relations[gr]['date'],
                             'num_sentences':global_relations[gr]['num_sentences'], 
                             'entities':len(global_relations[gr]['entities']),
                             'relations':len(global_relations[gr]['relations'])}
	#printflush("\nADD url_list with "+str(mongoid))
	#printflush(url_list[mongoid])

    return url_list

def make_network_one_out(fma,mc,center_entity,one_out_seen, one_out_nodes,exclude, new_skip, merge_ids, alias_to_master, debug=False):    
	#[ #links, #ent_id, #alias ids]    #links does not include those of aliases    #( they can be looked up via mc[mid] for now )
	
	#merge_ids_flat = []
	#for yv in merge_ids.values():
	#	for yy in yv:
	#		merge_ids_flat.append(yy)
	
	merge_ids_flat = [ yy for yv in merge_ids.values() for yy in yv ]  #this is more optimized than above but i could make it better.. what does merge_ids look like?

	final_net = {}
	#gcoleman = global_index["Garnet Coleman"]
	gcoleman = global_index[center_entity]
	if debug:
		printflush("Entity: "+center_entity)
		printflush("EntityID: "+str(gcoleman))
		printflush(fma)

	final_net[gcoleman] = fma
	for i,e in enumerate(fma):
		try:
			times, eid, aliases = e
		except:
			if debug:
				printflush("Error in unpacking.  e is of size: "+str(len(e)))
				printflush(e)
			
			if len(e) == 2:
				if debug:
					printflush("Size two so use as times, and eid")
				times, eid = e
				aliases = []
			else:
				if debug:
					printflush("NOT SIZE 2 so skip")
				continue

		glob = global_entities[eid]
		if debug:
			try:
				printflush("\n&&&&& at "+str(i)+": CURRENTLY HANDLING: "+glob["full_name"] + "("+glob["entity_type"]+", "+str(eid)+") - with aliases: "+str(aliases))            
			except:
				traceback.print_exc(file=sys.stdout)
		    
		x = entity_edges[eid]['edges']
		xf = [ [v[v.keys()[0]],v.keys()[0]] for v in x]
		most_assocatied = sorted(xf, reverse=True)
		most_assocatied_flat = [ m[1] for m in most_assocatied ]
		filt_most_assoc = []
		if debug:
			printflush("\tBEFORE FILTER/MERGING size: "+str(len(most_assocatied_flat)))
			       
                kfiltered =[ k for k in most_assocatied if k[1] != gcoleman and k[1] not in aliases and k[1] not in one_out_seen]
		#for k in most_assocatied:
		for k in kfiltered:
			#if k[1] == gcoleman or k[1] in aliases or k[1] in one_out_seen: 
				#if id is Garnet Colemans or one of our aliases or already has an edge with this k[1] from prior loops don't use
			#	continue
			
			ee = global_entities[k[1]]            
			if ee["full_name"] not in exclude and ee["full_name"] not in new_skip  and k[0] >= 2:   #maybe make this 3 smaller so you can get nodes farther out?
				if debug: # and i < 2:
					printflush("ADD: "+ee["full_name"] + "("+ee["entity_type"]+", "+str(k[1])+") - "+str(k[0])+" times")

			#NOW HANDLE ALIASES FOR K              
			if k[1] in merge_ids_flat:    
				if debug:
					printflush("\t XXX"+ee["full_name"]+" ... this record has been merged.. Check if it exists here and if not add it")
			
				if alias_to_master[k[1]] in most_assocatied_flat:                         
					if debug:
						printflush("----Yes it is so remove it")
				#del filt_most_assoc[i] # just don't append it
					continue 
				else:
					if debug:
						printflush("----No it isn't so add it by constructing a new k")
				k = [k[0],alias_to_master[k[1]],[k[1]]]
			else:                                           
				alias_list = []
				if k[1] in merge_ids:         #these are master ids               
					mids = merge_ids[k[1]]
					for mid in mids:
						alias_list.append(mid)
						ei = global_entities[mid]
						if debug:
							printflush("\t included merged: "+ei["full_name"] + "("+ei["entity_type"]+", "+str(mid)+")"+str(mc[mid])+" times")
					k.append(alias_list)    
				else:
					k.append(alias_list)  #allias list empty
			
			filt_most_assoc.append(k)  
			
			if k[1] not in one_out_nodes:
				one_out_nodes.append(k[1])  #at the end, one_out_node will be what we use to construct large nodes list, 
							#and final net will be used to make large edges list.
				
							#whereas near_entities_seen will be used to construct small nodes list
							#and filtered_most_associated will be used to make small edges list.

		final_net[eid] = filt_most_assoc  
		one_out_seen.append(eid)
		
	return final_net


def add_text_snippet(text):
    #give edge (source1-source2-exacthit) that contains snippet an index in text_snippets and return id 
    text_snippets.append(text)
    return len(text_snippets) - 1


def update_entity_counter_gn(source,target,debug=False):
    global entity_edges
    if debug:
        printflush("In Update Entity Counter")
    if source not in entity_edges:
        entity_edges[source] = {'counter':1,'edges':[{target:1}]}
    else:
        entity_edges[source]['counter'] = entity_edges[source]['counter'] + 1
        f = 0
        if debug:
            printflush("In Update Entity Source looking for "+str(target))
        for i,ed in enumerate(entity_edges[source]['edges']):                       
            if debug:
                printflush(ed)
                
            if ed.keys()[0] == target:  
                f = 1
                if debug:
                    printflush("Found "+str(target)+" so update counter!")
                #entity_edges[source]['edges'][target] = entity_edges[source]['edges'][target] + 1
                ed[ed.keys()[0]] = ed[ed.keys()[0]] + 1
                break
        if f == 0:
            if debug:
                printflush("Didn't find "+str(target)+" so add it")
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

'''
def update_entity_counter_new(source,target,debug=False): #OLD VERSION
    global entity_edges
    if source not in entity_edges:
        entity_edges[source] = {'counter':1,'edges':[{target:1}]}
    else:
        entity_edges[source]['counter'] = entity_edges[source]['counter'] + 1
        f = 0

        for i,ed in enumerate(entity_edges[source]['edges']):                       
            if debug: printflush(ed)
            if ed.keys()[0] == target:  
                f = 1
                #if debug: printflush("\tFound "+str(target)+" so update counter!")
                ed[ed.keys()[0]] = ed[ed.keys()[0]] + 1
                break

        if f == 0:
            #if debug: printflush("\tDidn't find "+str(target)+" so add it")
            entity_edges[source]['edges'].append({target:1})


    if target not in entity_edges:
        entity_edges[target] = {'counter':1,'edges':[{source:1}]}
    else:
        entity_edges[target]['counter'] = entity_edges[target]['counter'] + 1
        f = 0
        for i,ed in enumerate(entity_edges[target]['edges']):
            if ed.keys()[0] == source:
                f = 1
                ed[ed.keys()[0]] = ed[ed.keys()[0]] + 1
                break
        if f == 0:
            entity_edges[target]['edges'].append({source:1})
'''


def update_entity_counter_new(source,target,edge_lookup,debug=False):
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


def add_intermediate_json_relations_split(res,num_instances,debug=False):
    #THIS FUNCTION SPLITS BETWEEN SMALL VERSION WHICH WORKS QUICKLY FOR MOST CASES AND BIG ONE WHICH IS OPTIMIZED FOR BIG RESULT SETS
        
    global_rels = [res.copy()]        #this is just the relations for the current article ( and not cumulative from priors )    

    num_entities =  len(res['entities'])
    num_sents = res['num_sentences']
    prod = num_instances * num_entities * num_sents

    if prod > 8000:
	#do big way
    	if debug: printflush("\t**IN GENERATE ADD INTERMEDIATE JSON WITH insts: "+str(num_instances)+", ents: "+str(num_entities)+", sents: "+str(num_sents)+", and prod: "+str(prod)+ " ... CALL BIG")
        add_intermediate_json_relations_new(global_rels,debug)
    else:
    	if debug: printflush("\t**IN GENERATE ADD INTERMEDIATE JSON WITH insts: "+str(num_instances)+", ents: "+str(num_entities)+", sents: "+str(num_sents)+", and prod: "+str(prod)+ " ... CALL SMALL")
        add_intermediate_json_relations_gn(global_rels,debug)



def add_intermediate_json_relations_new(global_rels,debug=False):
    #this is newer version for BIG RESULT SETS
    global global_entities
    global edges_seen
    global json_output
    global entity_edges

    if debug:
        printflush("In ADD INTERMEDIATE Json Relations with number of relations: "+str(len(global_rels['relations'])))
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

    #possibly also make prelookup for main entity person ( so you don't have to go through their edges ).. but only if this is saves time
    source_lookup = {}
    edge_lookup = {}
    for i,e in enumerate(entity_edges):
	edge_lookup[e] = {k: n for n,ed in enumerate(entity_edges[e]['edges']) for k,v in ed.iteritems() }
	source_lookup[e] = set([k for ed in entity_edges[e]['edges'] for k,v in ed.iteritems()])


    if debug:
	printflush("Source Lookup")

    for i,gr in enumerate(global_rels):
        for r in gr['relations']:
            inst = {'source':r['term1_id'],'target':r['term2_id']}

	    grmid = str(gr['mongoid']).replace("ObjectId(","").replace(")",'') #can i not do this somehow
            ei = {'type':r['type'],'mongoid':grmid}
            ei['mongoid'] = grmid
	    if 'text_snippet' in r:
		textid = add_text_snippet(r['text_snippet'])
		ei['textid'] = textid
            
            inst['inst'] = [ei]

            #check if it exits, either source-target or target-source   #I CAN MAKE THIS FASTER (make a dictionary look up by source or target!
	    f = 0
	    if inst['source'] in entity_edges:
		if inst['source'] in source_lookup:
		    if inst['target'] in source_lookup[inst['source']]:  
			if debug: printflush("FOUND TARGET IN SOURCE_LOOKUP")
			f = 1
			s = inst['source']
			t = inst['target']
			#break
		else:
			if debug: printflush("DIDNT FIND inst[source] = "+str(inst['source'])+" in source_lookup")
			for i,ed in enumerate(entity_edges[inst['source']]['edges']):                       
			    if ed.keys()[0] == inst['target']:  
				f = 1
				s = inst['source']
				t = inst['target']
				break

	    elif inst['target'] in entity_edges:
		#if debug: printflush("Looking through "+str(len(entity_edges[inst['target']]['edges']))+" edges of target: "+str(inst['target'])+" for source: "+str(inst['source'])
		if inst['target'] in source_lookup:
		    if inst['source'] in source_lookup[inst['target']]:  
			if debug: printflush("FOUND SOURCE IN TARGET_LOOKUP <-- definitely not expecting this")
			f = 1
			s = inst['target']
			t = inst['source']
			#break
		else:
			if debug: printflush("DIDNT FIND inst[target] = "+str(inst['target'])+" in source_lookup")
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
				if debug: print "\tFound source: "+str(s)+" and target: "+str(t) +" in jso_lookup and it says its edge: "+str(jso_lookup[s][t])
				try:
					edg = json_output["elements"]["edges"][jso_lookup[s][t]]
					edg['data']['inst'].append(ei)
					update_entity_counter_new(s,t,edge_lookup,debug)
					#update_entity_counter_new(s,t,debug)  #old version

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
					update_entity_counter_new(s,t,edge_lookup,debug)

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

				update_entity_counter_new(inst['source'],inst['target'],edge_lookup,debug)

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

	    	update_entity_counter_new(inst['source'],inst['target'],edge_lookup, debug)

		s = inst['source']
		t = inst['target']
		if s in source_lookup:
			if t not in source_lookup[s]:
				if debug: print "UPDATE SOURCE LOOKUP COUNTER10: for source: "+str(s)+" found no target: "+str(t) +" in source_lookup so add it"
				source_lookup[s].add(t) 
		else:
			if debug: print "UPDATE SOURCE LOOKUP COUNTER12: source not found "+str(s)+" and found no target: "+str(t) +" in source_lookup so add it"
			source_lookup[s] = set([t])


def add_intermediate_json_relations_gn(global_rels,debug=False):
    global global_entities
    global edges_seen
    global json_output

    if debug:
        printflush("In Generate Add Intermediate Small Json Relations with number of relations: "+str(len(global_rels['relations'])))
	#print global_rels

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
    
    for i,gr in enumerate(global_rels):
        for r in gr['relations']:
            inst = {}
            inst['source'] = r['term1_id']
            inst['target'] = r['term2_id']
            ei = {}
            ei['type'] = r['type']
	    grmid = str(gr['mongoid']).replace("ObjectId(","").replace(")",'')   #NEW
            ei['mongoid'] = grmid
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

                #update_entity_counter_gn(s,t,debug)
                
	    '''
            else:
                #THIS IS TO PREVENT ADDING LOCATION RELATIONS
                #if global_entities[inst['source']]['entity_type'] != "LOCATION" and global_entities[inst['target']]['entity_type'] != "LOCATION":
		edges_seen.append([inst['source'],inst['target']])                    
		json_output["elements"]["edges"].append({"data":inst})
		new_edges['edges'].append({"data":inst})                    
		update_entity_counter_gn(inst['source'],inst['target'],debug)
	    '''
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
					update_entity_counter_gn(s,t,debug)  #compare against small

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
					json_output["elements"]["edges"].append({"data":inst})  
					jso_lookup[s][t] = len(json_output["elements"]["edges"]) - 1  
					new_edges['edges'].append({"data":inst})                    
					update_entity_counter_gn(s,t,debug)

			else:
				#didn't find in look up table but add anyways ( why wasn't it found )
				json_output["elements"]["edges"].append({"data":inst})  
				if inst['source'] in jso_lookup:
					if inst['target'] in jso_lookup[inst['source']]:
						printflush("REALLY SHOULDNT HAVE GOTTEN HERE")
						reallyshouldnthavegottenhere = 1
					else:
						jso_lookup[inst['source']][inst['target']] = len(json_output["elements"]["edges"]) - 1			
				else:
						jso_lookup[inst['source']] = {inst['target']: len(json_output["elements"]["edges"]) - 1 } 			

				new_edges['edges'].append({"data":inst})                    
				update_entity_counter_gn(inst['source'],inst['target'],debug)

            else:
	    	json_output["elements"]["edges"].append({"data":inst})  
		if inst['source'] in jso_lookup:
			if inst['target'] in jso_lookup[inst['source']]:
				reallyshouldnthavegottenhere = 1
			else:
				jso_lookup[inst['source']][inst['target']] = len(json_output["elements"]["edges"]) - 1			
		else:
				jso_lookup[inst['source']] = {inst['target']: len(json_output["elements"]["edges"]) - 1 } 			

	    	new_edges['edges'].append({"data":inst})                    
	    	update_entity_counter_gn(inst['source'],inst['target'],debug)

                    





def construct_large_json_take3(smj,final_net,center_entity,larger_relations,debug):
	
	large_debug = False #by default don't show large debugging info
	if debug:
		large_debug = True
	
	if large_debug:
		printflush("XXXX IN CONSTRUCT LARGE JSON TAKE3:   smj = ")
		#printflush(smj)
		printflush("XXXX LARGER_RELATIONS = ")
		#printflush(larger_relations)   ##WHY IS THIS EMPTY FOR BOB
		printflush("XXXX NOW VERIFY AND SAVE LARGE")

	#NEED TO RESET THESE
	#edges_seen.append([inst['source'],inst['target']])                    
	#json_output["elements"]["edges"].append({"data":inst})
	#new_edges['edges'].append({"data":inst})                    
	#update_entity_counter(inst['source'],inst['target'],debug)
	global json_output
	global edges_seen
	global text_snippets
	global entity_edges
	json_output = {"elements":{"nodes":[],"edges":[]}}
	edges_seen = []      #just used to see whether an edge has already been added
	text_snippets = []   #keeps track of text snippets
	entity_edges = {}    #used as lookup to see how many edges an entity has and where they are located.


	#Testing Bob Hall
	#printflush("XXXX IN CONSTRUCT LARGE JSON TAKE3:   smj = ")
	#printflush(smj)
	numarts = len(larger_relations) 
	printflush("IN LARGER_RELATIONS:  With "+str(numarts)+" worth of articles to add relationships for")    #indexed by URL and gives res ( from verify_and_ ) for each one

	#larger_verified = {}
	
	lgstart = time.clock()
	for nurl, lurl in enumerate(larger_relations):
		lcontent = larger_relations[lurl]
		if large_debug:
			printflush("\nVVVVV lurl: ")
			printflush(lurl)
			printflush("XXXX Lcontent")
			#printflush(lcontent)
			printflush("XXXX len")
			printflush(str(len(lcontent)))
		
		#HMMM?? I USUALLY PASS IN NUMBER OF INSTANCES OF MAIN GUY AS 2nd param here.. what do i do now?
		try:
			''' 
			lcontent = {'num_sentences': 7, 'date': '2015-04-22', 'url': u'http://www.statesman.com/ap/ap/texas/red-light-cameras-could-be-finished-in-texas/nkzxm/', 'relations': [], 'entities': {'Bob Hall': {'position': [u'Senator'], 'entity_type': 'PERSON', 'id': [3, 7, 8], 'sentence': [1, 5, 6]}}, 'mongoid': '556446b2dabb4f5450e1393e'}
			'''
			#num_instances = len(lcontent['relations'][0])
			ents = lcontent['entities']
			main_node = ents.keys()[0]
			num_instances = len(ents[main_node]['sentence'])
		except:
			traceback.print_exc(file=sys.stdout)
			printflush("ERROR on "+str(nurl)+": Couldn't Find num_instances.  What is 'relations' index of lcontent?")
			printflush("lcontent = ")
			printflush(lcontent)
			
		aistart = time.clock()
		add_intermediate_json_relations_split(lcontent,num_instances,False)    
		aiend = time.clock()
		try:
			printflush("\ton "+str(nurl)+" of "+str(numarts)+" took "+str(aiend - aistart)+" seconds.  URL: "+lurl+" with "+str(num_instances)+" instances and "+str(len(ents))+" entities")
		except:
			printflush("error: couldn't print out")
			traceback.print_exc(file=sys.stdout)
			sys.exit()
			
	lgend = time.clock()
	totlg = (lgend - lgstart)/60
	printflush("TIME INFORMATION: all add_intermediates took "+str(totlg)+" minutes!")

	if large_debug:
		printflush("\nQQQQQ AFTER ALL ADD_INTERMEDIATES")
		#printflush(json_output)    #important
		printflush("\nglobal index:")
    		printflush(global_index) 
		printflush("\nentity_edges:")
		#printflush(entity_edges) 
		printflush("\nglobal_entities:")
		#printflush(global_entities)
		printflush("\nedges seen:")
		#printflush(edges_seen)

	large_json_output = copy.deepcopy(smj)
	possible_edges = copy.deepcopy(json_output["elements"]["edges"])    #copy by value, not reference

	gcoleman_id = global_index[center_entity]
	one_away = set([k[1] for k in final_net[gcoleman_id]])
	#soutars = [ [k['source'], k['target']] for k in large_json_output['elements']['links']]  #can't make this a set
	soutars = {}
	for k in large_json_output['elements']['links']:
		try:
			soutars[k['source']].append(k['target'])
		except:
			soutars[k['source']] = [k['target']]

	if large_debug == large_debug:
		printflush("Center Entity: "+center_entity+" with id: "+str(gcoleman_id)+"\n")     #Kyle Janek 502
		printflush("Nodes in json_ouput: "+ str(len(large_json_output['elements']['nodes'])))
		printflush("Number of edges in json_output: " + str(len(large_json_output['elements']['links'])))
		printflush("XXXX ONE AWAY PEOPLE: "+str(len(one_away)))
		printflush("XXXX POSSIBLE EDGES TO SELECT FROM ( "+str(len(possible_edges))+" from which we need to select all whose source/target are in one_away)")
		printflush("********************")
		printflush("Populate edges!")

	text_ids_needed_for_demo = {}
	pestart = time.clock()
	count = 0 #for debuging only

	po_edgesfiltered = [ edg for edg in possible_edges if edg["data"]["source"] in one_away and edg["data"]["target"] in one_away and edg["data"]["source"] != gcoleman_id and edg["data"]["target"] != gcoleman_id]

	#for e,edg in enumerate(possible_edges):
	for e,edg in enumerate(po_edgesfiltered):
		try:
			sid = edg["data"]["source"]
			tid = edg["data"]["target"]
			#if (sid not in one_away or tid not in one_away) or (sid == gcoleman_id or tid == gcoleman_id):            
			for tee in edg["data"]["inst"]:
				try:
					if 'textid' in tee:
						if tee["textid"] not in text_ids_needed_for_demo:
							#text_ids_needed_for_demo.append(tee["textid"])
							text_ids_needed_for_demo[tee["textid"]] = 1
					tee["mongoid"] = str(tee["mongoid"]).replace("ObjectId(","").replace(")",'')
				except:
					printflush("ERROR: ")
					traceback.print_exc(file=sys.stdout)
					printflush(edg)
					printflush("Edge #"+str(e)+" of "+str(len(po_edgesfiltered)))
					sys.exit()

			#CHECK IF LINK ALREADY IN LINKS:: 
			#if [sid,tid] not in soutars:
			if sid not in soutars:
				if large_debug:
					printflush("PRE-ADD LINK "+global_entities[sid]['full_name']+" ("+str(sid)+") - "+global_entities[tid]['full_name']+" ("+str(tid)+")")
					printflush(edg['data'])

				large_json_output["elements"]["links"].append(edg['data'])
				count = count +1 
				soutars[sid] = [ tid ]  
			elif tid not in soutars[sid]:
				large_json_output["elements"]["links"].append(edg['data'])
				count = count +1 
				soutars[sid].append(tid) #since now set for quicker lookup
		except:
			printflush("error")
			traceback.print_exc(file=sys.stdout)
			noting = 1
	
        text_ids_needed_for_demo = set(text_ids_needed_for_demo)
	peend = time.clock()
	totpe = (peend - pestart)/60
	printflush("TIME INFORMATION: looping through possible edges took "+str(totpe)+" minutes!")
	
	if large_debug == large_debug:
		printflush("PPPPPPP   AFTER EVERYTHING!!")
		printflush("XXXXNODES ("+str(len(large_json_output['elements']['nodes']))+")")
		printflush("XXXXLINKS ("+str(len(large_json_output['elements']['links']))+") [ source, target ]" )
		printflush("Count: "+str(count))
		#printflush(large_json_output['elements']['nodes'])
		#print [ [k['source'], k['target']] for k in large_json_output['elements']['links']]
		#print large_json_output

	onetofivestart = time.clock()
	lg_jo = large_json_output

	#i could stand to make this all more efficient .. make this a set
	#1.  only include nodes which are definitely linked to!!  
	all_link_nodes = []
	for i, e in enumerate(lg_jo['elements']['links']):
	    if e['source'] not in all_link_nodes:
		if large_debug:
			printflush("ADD source: "+str(e['source']))
		all_link_nodes.append(e['source'])
		
	    if e['target'] not in all_link_nodes:
		if large_debug: 
			printflush("ADD target: "+str(e['target']))
		all_link_nodes.append(e['target'])

	if large_debug:
		printflush("AFTER 1")
		#print len(all_link_nodes)  #353 if this is working correctly!

	#2.  remove nodes not in all_link_nodes
	newnodes = []
	for i,n in enumerate(lg_jo['elements']['nodes']):
	    if n['id'] in all_link_nodes:
		newnodes.append(n)
	    else:
		if large_debug:
			printflush(str(i)+": didn't find the following in all_link_nodes: "+str(n['id'])+" so remove it")
		
	if large_debug:
		printflush("AFTER 2")
		printflush("nnodes: ",len(newnodes))  #there should be no "didn't find messages!"
		#print newnodes

	#3.  make dict from entid to nodes index id
	entid_to_node = {}
	index_to_endit = {}
	for i,n in enumerate(newnodes):
		entid_to_node[n['id']] = i
		index_to_endit[i] = n['id']

	if large_debug:
		printflush("AFTER 3")
		printflush("Entid_to_node")
		printflush(entid_to_node)


	#4.  and then change all links to use them!
	newlinks = copy.deepcopy(lg_jo['elements']['links'])
	for i,e in enumerate(newlinks):		
		if e['source'] not in entid_to_node:
			printflush("Source: "+ str(e['source']) + " not found in entid_to_node")
		else:
			if e['target'] not in entid_to_node:
				printflush("Target: "+ str(e['target']) + " not found in entid_to_node")
				
			else:
				e['source'] = entid_to_node[e['source']]
				e['target'] = entid_to_node[e['target']]

	#5.  change sm to use new nodes and new links
	lg_jo["elements"]["nodes"] = newnodes
	lg_jo["elements"]["links"] = newlinks


	onetofiveend = time.clock()
	tototf = (onetofiveend - onetofivestart)/60
	printflush("TIME INFORMATION: doing steps 1 to 5 took "+str(tototf)+" minutes!")

	tottime = tototf + totpe + totlg
	printflush("EN RESUMEN: TIME INFO:  large construction took "+ str(tottime) +" minutes of which ADD_INT TOOK: "+str(totlg / tottime)+" %,  POSSIBLE_EDGES TOOK: "+str(totpe/tottime)+" % and END STEPS TOOK: "+str(tototf/tottime)+"%")
	#TODO: SO WHAT TOOK THE LONGEST AND CAN I SPEED IT UP.. I'm assuming its the ADD_INST STAGE

	return [lg_jo,text_ids_needed_for_demo ]





#whereas near_entities_seen will be used to construct SMALL nodes list
#and filtered_most_associated will be used to make small edges list.
def construct_small_json(near_entities_seen,filtered_most_associated, center_entity):
    #printflush("in small json"
    small_json_output = {"elements":{"nodes":[],"links":[]}}
    possible_edges = copy.deepcopy(json_output["elements"]["edges"])   #copy by value, not reference
    #gcoleman_id = global_index["Garnet Coleman"]
    gcoleman_id = global_index[center_entity]

    
    fa = copy.deepcopy(filtered_most_associated)
    nes = copy.deepcopy(near_entities_seen)
    nes.append(gcoleman_id)
    
    #populate nodes
    for i,gid in enumerate(nes):
	gent = global_entities[gid].copy()
	
	if "id" in gent:
		del gent["id"]
	else:
		nothing = 1
		#printflush("ERROR: ID not found in gent: ")
		#printflush(gent)

	if "_id" in gent:
	    del gent["_id"]
	    
	gent["id"] = gid

	if 'sentence' in gent:
	    del gent['sentence']
	    
	#small_json_output["elements"]["nodes"].append({"data":gent})   #add nodes, make sure entity_type is here
	small_json_output["elements"]["nodes"].append(gent)   #add nodes, make sure entity_type is here
	  
    #populate edges
    fma_flat = [ f[1] for f in fa]
    text_ids_needed_for_demo = []
    
    #print len(possible_edges)
    #printflush("GColeman: "+str(gcoleman_id)
    #print filtered_most_associated_flat
    
    
    count = 0 #for debuging only
    for e, edg in enumerate(possible_edges):
				       
	#only include Garnet Coleman as source and  
	sid = edg["data"]["source"]
	if sid != gcoleman_id:            
	    #print str(e)+": Delete cause source ain't GC! "+str(sid)
	    #del small_json_output["elements"]["edges"][e]
	    nothing = 1
	    tid = edg["data"]["target"]
	    #if tid == 496:
	    #    printflush("!!!!!!!!!SKIPPED RICK PERRY"
	    #    print edg
	else:             
	    #check that target is in filtered_most_associated_flats (ie, those with GC).  if not get rid of it
	    tid = edg["data"]["target"]
	    #if tid == 496:
	#	printflush("Will Rick Perry make the cut?")
	    if tid not in fma_flat: #filtered_most_associated_flat:                
		#print str(e)+": Delete cause target ain't in! "+str(tid)
		#del small_json_output["elements"]["edges"][e]
		nothing = 1
	    else:
		#print str(e)+": Add edge with sid: ("+str(sid)+" and tid: "+str(tid)+")"
		#if tid == 496:
		#    printflush("!!!!!!!!!ADD RICK PERRY"
		#    print edg
		    
		#small_json_output["elements"]["edges"].append(edg)
		#{'mongoid': ObjectId('553ba8bf5a5b836d2fbb6180'), 'textid': 193845, 'type': 'near'},
		
		for tee in edg["data"]["inst"]:
		    if "textid" not in tee:
			#printflush("Error:  textid not found in tee")
			#printflush(tee)
			continue

		    if tee["textid"] not in text_ids_needed_for_demo:
			text_ids_needed_for_demo.append(tee["textid"])
		    
		    tee["mongoid"] = str(tee["mongoid"]).replace("ObjectId(","").replace(")",'')
		small_json_output["elements"]["links"].append(edg['data'])
		count = count +1 
		#for tee in edg["data"]["inst"]:
		#    if tee["textid"] not in text_ids_needed_for_demo:
		#	text_ids_needed_for_demo.append(tee["textid"])
    
    #printflush("Count: "+str(count)
    return [small_json_output,text_ids_needed_for_demo ]



def handle_photos(entity,ns,sm_jo,debug):
	currentphoto = "";
	currentwiki = "";
	found = -1
	try:
		if debug: printflush("Looking up prior values for "+entity)
		prior_photo_url = "";
		prior_wiki_url = "";
		for n in ns:
			if n["full_name"] == entity:
				if "photo_url" in n:
					prior_photo_url = n["photo_url"]
					if prior_photo_url == "":
						prior_photo_url = "no photo url previously found"  #this is new
				else:
					#printflush("No prior photo found so!")
					nothing = 1

				if "wiki_stub" in n:
					if n["wiki_stub"] == "no wiki page":
						prior_wiki_url = "no wiki page"
					else:
						prior_wiki_url = n["wiki_stub"]
				else:
					if debug: printflush("--CALLING get_wiki_link for "+ n["full_name"] + ".. was this necessary?")
					prior_wiki_url = get_wiki_link(entity)   #make sure you only do this if you have "" or no "wiki_stub"
					if prior_wiki_url == "":
						prior_wiki_url = "no wiki page"
				
				if prior_photo_url == "":
					if prior_wiki_url != "" and prior_wiki_url != "no wiki page":
						#get stub only if you have too!
						wikistub = prior_wiki_url.split("/")[-1]
						if debug: printflush("--CALLING get_wiki_photo for "+ n["full_name"] + " with wikistub: "+wikistub+".. was this necessary?")
						prior_photo_url = get_wiki_photo(wikistub)
					else:
						prior_photo_url = "images/bluedot.png";
 
				break

		#printflush("Prior Photo URL: "+prior_photo_url)
		if prior_photo_url != "":
			for i,no in enumerate(sm_jo["elements"]["nodes"]):
				if no["full_name"] == entity:
					if "photo_url" not in no:      #only rewrite it if it doesn't have one
						sm_jo["elements"]["nodes"][i]["photo_url"] = prior_photo_url
						currentphoto = prior_photo_url
						found = i
						break
					else:
						currentphoto = no["photo_url"]
				
					if "wiki_stub" not in no:
						#if prior_wiki_url != ""  #only rewrite new value if one doesn't exist for it
						sm_jo["elements"]["nodes"][i]["wiki_stub"] = prior_wiki_url
						currentwiki = prior_wiki_url
					else:
						currentwiki = no["wiki_stub"]

					if debug: printflush("--- Assign "+no["full_name"]+" photourl: "+ currentphoto + " and wiki_stub: "+ currentwiki)
		
	except:
		printflush("Warning: Couldn't complete prior photourl/prior wiki_url for "+entity)
		traceback.print_exc(file=sys.stdout)

	return [found,currentphoto,currentwiki,sm_jo]


def generate_single_network(also_larger,center_entity,debug,load_pickle = False):
	'''
	global_entities = global_entities()                   xxxx
	global_relations = globalobjs.global_relations		ADD
	article_relations = globalobjs.article_relations      no need
	global_index = globalobjs.global_index               xxxx    
	json_output = globalobjs.json_output                  xxxxx
	edges_seen = globalobjs.edges_seen                    no need
	text_snippets = globalobjs.text_snippets              ADD
	entity_edges = globalobjs.entity_edges                 xxxx
	url_texts = globalobjs.url_texts			no need
	'''
	if center_entity == "J.D. Sheffield":
		center_entity = "Sheffield"

	gsn_start = time.clock()
    	global global_index     #indexed by Entity Name and gives the id of that node...                ex. global_index['Kyle Janek'];   #502
	global entity_edges     #indexed by NodeID and provided edges for it 			        ex. entity_edges[502];  {'counter': 15370, 'edges': [{488: 98}, {499: 284}, {487: 2}, ... }
	global global_entities  #indexed by NodeID and provides full_name, entity_type , etc for node.  
				#			     ex. global_entities[502] {'entity_type': 'PERSON', 'full_name': 'Kyle Janek', 'id': [13], 'position': [u'incumbent'], 'sentence': [6]}
	global json_output      #constructed prior json output.  ex.  json_output['elements']['nodes'] is empty.. whereas json_output['elements']['edges'] contains all the elements in entity_edges 
				#                            ex.  len(json_output['elements']['edges']) #41887, 
				#                            ex.  In [29]: json_output['elements']['edges'][0]
				#{'data': {'inst': [{'mongoid': ObjectId('553ba68a5a5b836c8bc2df9d'), 'textid': 0, 'type': 'near'}, ......
				#	 	    {'mongoid': ObjectId('553ba8be5a5b836d2fbb6168'), 'textid': 192365, 'type': 'near'}],
				#          'source': 502, 'target': 488}}

	global text_snippets    #indexed by TextID from json_output and gives back text snippet
	global global_relations #indexed by URL, 
				#global_relations.keys()[0]   #u'http://www.chron.com//news/article/Parents-may-decide-if-twins-separated-in-school-1529761.php'
				#global_relations[global_relations.keys()[0]]
				#{'date': u'March', 'entities': {'Austin': {'entity_type': 'LOCATION', 'id': [7, 20], 'sentence': [7, 21]},
				#				 'Bradford Shields': {'entity_type': 'PERSON', 'full_name': 'Bradford Shields', 'id': [17], 'sentence': [20]},
				#		 		 'Cal State-Fullerton': {'entity_type': 'LOCATION', 'full_name': 'Cal State-Fullerton', 'id': [15], 'sentence': [18]},
				#'num_sentences': 25,
 				#'relations': [{'distance': '2', 'sentence_num': [1, 3], 'subtype': 'prior', 'term1': 'Kyle Janek', 'term1_id': 502, 'term2': 'Texas', 'term2_id': 497,
   				#	         'text_snippet': u'School principals... Kyle Janek, R-Houston, asked incredulously Thursday.',
   				#                'type': 'near'}, .... ]
				#'url': u'http://www.chron.com//news/article/Parents-may-decide-if-twins-separated-in-school-1529761.php'}
	global url_list
	global larger_relations

	if load_pickle == True:
		#TODO load from a tar.gz file by untarring file, loading things, and then deleting untarred file!
		
		crr = center_entity.replace(" ","_")
		#look for tar.gz file, if doesn't exist look for picke, otherwise fail
		tarf = datap + "data/pickles/"+crr+".tar.gz"
		picklefile = datap + "data/pickles/"+crr+".pickle"
		if os.path.isfile(tarf):
			tarstart = time.clock()
			printflush("Found tarfile: "+tarf+" so extract pickle file from it")
			tar = tarfile.open(tarf)
			#tar.extractall()
			member = tar.getmembers()[0]
			member.name = "/" + member.name
			tar.extract(member)
			tar.close()
			tarend = time.clock()
			printflush("TIME INFO:  time spent untarring file: "+str(tarend - tarstart)+" seconds")
			#move(crr+".pickle",picklefile)

			if os.path.isfile(picklefile):
				printflush("Load picklefile: "+picklefile)
				pklstart = time.clock()
				with open(picklefile,'rb') as f:
					global_index, entity_edges, global_entities, center_entity, json_output, text_snippets, global_relations, url_list, larger_relations = pickle.load(f)

				pklend = time.clock()
				printflush("TIME INFO:  time spent loading pickle file: "+str(pklend - pklstart)+" seconds")

		elif os.path.isfile(picklefile):
			printflush("Load picklefile: "+picklefile)
			with open(picklefile,'rb') as f:
				global_index, entity_edges, global_entities, center_entity, json_output, text_snippets, global_relations, url_list, larger_relations = pickle.load(f)
		else:
			printflush("ERROR OPENING FROM FILE!")
			sys.exit()
			
		if not os.path.isfile(tarf):
			#make tar
			printflush("Make tar file: "+tarf+" and save pickle to it")
			tar = tarfile.open(tarf, "w:gz")
			tar.add(picklefile)
			tar.close()
		
		if os.path.isfile(tarf):
			#rm pickle after you are sure backup exists
			printflush("Delete picklefile: "+picklefile)
			os.remove(picklefile)
		
			
			
		pickle_end = time.clock()
		printflush("TIME INFO: To open tar, pickle, etc it took: "+str(pickle_end - gsn_start)+" seconds")

		
	single_debug = False ####################this controls debug for small network
	if debug:
		single_debug = True

	#goid = global_index["Garnet Coleman"]
	goid = global_index[center_entity]
	printflush("Center_entity: "+center_entity+" with id: "+str(goid))
	printflush("Global Entites: "+str(len(global_entities)))
	printflush("Global Relations: "+str(len(global_relations)))
	printflush("Larger Relations: "+str(len(larger_relations)))
	
	printflush("ENTITY EDGE KEYS: "+str(len(entity_edges.keys())))
	#print entity_edges
	x = entity_edges[goid]['edges']
	xf = [ [v[v.keys()[0]],v.keys()[0]] for v in x]
	most_assocatied_with_garnet_coleman = sorted(xf, reverse=True)

	#for Kyle Janek
	#[ global_entities[v[1]]['full_name'] for v in most_assocatied_with_garnet_coleman[0:20] ]
	#['Metro', 'Senate', 'Republican', 'House', 'Republican Rick Perry', u'Garnet Coleman', 'Legislature', 'Medicaid', 'Chris Bell', u'Scott Hochberg', 'Greg Abbott', 'Republicans', 
	#  'HHSC', u'Rodney Ellis', u'John Whitmire', 'Health and Human Services Commission', 'Texas House', 'Democrats', 'GOP', u'Joan Huffman']


	if single_debug:
		printflush( x )
		printflush( most_assocatied_with_garnet_coleman )

	filtered_most_associated = []
	'''
	exclude = ["Democrats","Democratic","Democrat","Houston Democrat","Houston Democrats","House Democratic","Houston-area","Houston Democratic","Democratic Representatives",
		   "Republican","Republicans","Republican House","GOP","Republican Party","Justice","US","Texans","Houstonians","House Republicans",
		   "House","two House","House floor","Senate","Congress","Texas Legislature","Legislature","Chronicle","State Senate","House Aug","Legislative",
		   "House of Representatives","House Majority","Houston Chronicle","The Chronicle","Democrat Garnet Coleman","Obama Clinton",
		   "American","janet .","chris .","Internet","University","The House","P.O.","contrast Bell","Council","Colemans",
		   "Democrats Craddick","Tier","chairmen Pitts","Texas-Mexico","African-American","African-Americans","Capital",
		   "Walt","Congressman Ryan","ID","Montessori","Bills","Taser","Tasers"]
	'''
	exclude = []

	for k in most_assocatied_with_garnet_coleman:
	    ee = global_entities[k[1]]    
	    if ee["full_name"] not in exclude  and k[0] >= 1:    #THIS ONLY INCLUDES RELATIONSHIPS SEEN 1 OR MORE TIMES!  don't filter!!
		if single_debug:
			try:
				#printflush("ADD: "+ee["full_name"] + "("+ee["entity_type"]+", "+str(k[1])+") - "+str(k[0])+" times"
				nothing = 1
			except:
				printflush("ERROR printing out something in ee or k")
				printflush(ee)
				printflush(k)
				traceback.print_exc(file=sys.stdout)
		filtered_most_associated.append(k)

	if single_debug:
		printflush("BEFORE MERGING size: "+str(len(filtered_most_associated)))  #368 direct connections before doing merging (which will bring it to 360ish)

	backup_of_filtered = copy.deepcopy(filtered_most_associated)   

	# SPECIFIC GARNET COLEMAN MERGE FUNCTIONALITY
	#FOR NOW JUST DO MERGING LOCALLY AND keep track of equivalent ent_ids somehow
		 #change id[0] for id[1]  so make sure id[0] has less hits then id[1] and then remove id[1] from list

	'''
	if center_entity == "Garnet Coleman":
		merge = [("Texas Southern University","TSU"),("Governor Perry","Rick Perry"),("Medicaid-related","Medicaid"),
			 ("University of Houston","UH"),("University of Texas","UT"),("young Medical Center","Medical Center"),
			 ("DENVER Barack Obama","Barack Obama"),("Bush","George W. Bush"),
			 ("Democrat Bill White","Bill White"),("R-Pampa Craddick","Tom Craddick"),("Craddick Craddick","Tom Craddick"),
			 ("Craddick Ds","Tom Craddick"),("Tom Craddick House","Tom Craddick"),("Shelia Jackson Lee , state Representatives","Shelia Jackson Lee"),
			 ("Democrat Borris Miles","Borris Miles"),("Houston Independent School District","HISD"),
			 ("Delaware Hillary Clinton","Hillary Rodham Clinton"),("Health and Human Services","Texas Health and Human Services Commission"),
			 ("Health and Human Services Commission","Texas Health and Human Services Commission"),("Texas Health and Human Services","Texas Health and Human Services Commission"), 
			 ("Buice","Jon Buice"),("Fourth Ward Management District","Fourth Ward"),
			 ("Children 's Health Insurance Program","CHIP"),("Democrat Tony Sanchez","Tony Sanchez"),
			  ("Texas Department of Transportation","TxDOT"),("Democratic Gerry Birnberg","Gerald Birnberg"),
			 ("HHSC","Texas Health and Human Services Commission"),("Democrat Sylvester Turner","Sylvester Turner") ]
	else:
	'''
	merge = []

	#("Democratic Mario Gallegos","Mario Gallegos Jr"),
	merge_ids = {}
	for m in merge:
	    #merge_ids.append[(global_index[m[0]],global_index[m[1]])]
	    if global_index[m[1]] in merge_ids:
		merge_ids[global_index[m[1]]].append(global_index[m[0]])
	    else:
		merge_ids[global_index[m[1]]] = [global_index[m[0]]]
	 

	 
	merge_ids_flat = []
	for yv in merge_ids.values():
	    for yy in yv:
		merge_ids_flat.append(yy)

	merge_cnts = {}
	for k in filtered_most_associated:
	    if k[1] in merge_ids_flat:
		merge_cnts[k[1]] = k[0]
	    
	if single_debug:
		printflush("MERGE INFO")
		printflush(merge_ids )
		printflush( merge_cnts)
	prealias = copy.deepcopy(filtered_most_associated)

	#INCLUDE ALIAS SECTION
	for i,k in enumerate(filtered_most_associated):
	    ee = global_entities[k[1]]
	    if k[1] in merge_ids_flat: 
		    
		if single_debug:
			printflush("\tat i: "+str(i)+" GET RID of id ("+str(k[1])+") "+ee["full_name"]+" ... this record has been merged")
		
		del filtered_most_associated[i]  #MAYBE DON'T DO THIS CAUSE RICK PERRY LINKS ARE GOING MISSING
	    else:        
		#print ee["full_name"] + "("+ee["entity_type"]+", "+str(k[1])+") - "+str(k[0])+" times"
		alias_list = []
		if k[1] in merge_ids:                        
		    mids = merge_ids[k[1]]
		    for mid in mids:
			alias_list.append(mid)
			ee = global_entities[mid]
			if single_debug:
				printflush("\t included merged: "+ee["full_name"] + "("+ee["entity_type"]+", "+str(mid)+")"+str(merge_cnts[mid])+" times")
		    k.append(alias_list)    
		else:
		    k.append(alias_list)  #allias list empty

	if single_debug:
		printflush("AFTER MERGING size: "+str(len(filtered_most_associated)))

	near_entities_seen = []   #for nodes
	for i,e in enumerate(filtered_most_associated):
	    if e[1] not in near_entities_seen:
		near_entities_seen.append(e[1])


	alias_to_master = {}
	for k in merge_ids:
	    for v in merge_ids[k]:
		alias_to_master[v] = k

	'''
	new_skip = ["civic",", Precinct", "Aggie", "Anthony Hall;", "BP", "Buice", "Coordinating Board", "Deeply-versed", 
		    "Democrats Alma Allen", "Democrats alike", "Environmental Regulation", "Fair Houston", 'George " Mickey', 
		    "Governor Perry", "Greater Southeast", "Hispanic Democratic", "Houston Democrats" , "Representatives", 
		    "Houstonian", "LARA", "Latino", "Legislature Perry", "Lexicon", "Mickey Mouse", "Miss Thompson", 
		    "National Alliance", "Perry Hispanic", "Place", "Politics", "Republican-dominated", "Ron Green;", 
		    "Scott Street", "Shelia Jackson Lee , state Representatives", "Spanish", "Spanish", "Tom Craddick House", 
		    "United", "Urban", "and Democratic Representatives", "majority-GOP Legislature", "nearby University", 
		    "north of Memorial Drive", "with Precinct","To Coleman", "Tribune", "Texas Democrats", "Both Coleman", 
		    "Texas Tribune Festival","RSVP",  "Jon Buice", 'Doc " Anderson', 'Mexican', 'Channel', 'Texas Politics',
		    "Added Coleman", "Attorney", "Dallas Morning News", "Perry Hispanic", "Austin American-Statesman", 
		    "Latino", "Texas Politics","Place","Republican Dominated","Laura Bush Opens","Dallas; Ray Allen","Jones",
		    "Mando","Channel","Clinton Obama","Added Coleman","Both Coleman","To Coleman"]
	'''
	new_skip = []


	gstart = time.clock()
	#Then Build network from them
	one_out_seen = []
	one_out_nodes = copy.deepcopy(near_entities_seen)  #you do this to pass a copy of near entities and not reference to it!


	prelong = copy.deepcopy(filtered_most_associated)  #use this maybe to generate short json
	final_net = make_network_one_out(filtered_most_associated,merge_cnts,center_entity,one_out_seen, one_out_nodes,exclude, new_skip, merge_ids, alias_to_master, single_debug)

	
	gmake_net = time.clock()
	printflush("\nIMPORTANT TIME INFO, Make Network took : "+str(gmake_net - gstart))   #THIS CAN TAKE LONG SOMETIMES SO LOOK INTO MAKING IT MORE EFFICIENT

	#final_net
	# ",".join([str(v) for v in sorted(final_net.keys())])
	#'185,186,188,189,190,191,193,194,195,196,197,198,201,208,209,212,214,215,221,222,228,229,230,233,234,256,261,262,267,283,285,286,292,293,294,298,299,311,315,336,337,347,357,367,392,399,403,410,412,413,414,418,421,422,423,424,427,429,431,442,445,449,450,455,457,458,460,461,462,463,464,465,466,467,468,469,471,472,473,474,475,477,479,480,481,482,499,500,501,502,507,508,509,517,518,524,525,526,527,528,532,538,540,543,551,553,554,557,559,561,562,573,574,576,577,578,579,580,581,583,584,585,589,591,593,598,615,617,619,621,632,634,635,638,640,641,643,645,646,647,648,649,650,651,657,660,665,668,670,671,672,676,677,682,684,685,687,689,691,694,695,696,699,702,703,704,706,714,717,718,721,722,723,724,725,732,735,743,746,747,753,754,757,760,761,763,768,777,784,787,790,800,803,804,805,806,807,808,814,818,820,821,822,823,843,844,847,853,857,871,873,901,902,909,919,924,925,927,933,934,937,938,946,957,962,963,965,970,978,979,983,984,987,988,990,991,992,993,997,1001,1022,1039,1040,1043,1049,1050,1051,1099,1106,1107,1108,1152,1154,1157,1161,1162,1168,1171,1172,1176,1179,1186,1193,1204,1205,1213,1216,1221,1227,1253,1257,1275,1297,1298,1299,1300,1301,1302,1303,1304,1306,1310,1315,1316,1326,1327,1333,1338,1347,1349,1353,1354,1357,1379,1381,1382,1383,1384,1406,1408,1422,1477,1484,1485,1493,1498,1503,1504,1507,1513,1515,1517,1518,1521,1522,1523,1525,1527,1530,1533,1549,1557,1565,1579,1592,1606,1608,1630,1632,1633,1634,1635,1653,1697,1700,1709,1720,1721,1722,1730,1754,1802,1804,1809,1810,1813,1815,1817,1822,1832,1834,1837,1841,1860,1867,1868,1869,1870,1883,1892,1895,1896,1909,1924,1935,1988,1993,1997,1998,2002,2014,2044,2111,2145,2162,2174,2187,2230,2240,2285,2286,2315,2330,2390,2395,2421,2428,2431,2483,2512,2522,2612,2676,2700,2710,2751,2756,2758,2763,2778,2805,2825,2835,2896,2906,2909,2915,2928,2930,2951,2964,2966,2971,2977,2983,3005,3030,3064,3075,3125,3127,3149,3151,3176,3179,3201,3202,3212,3230,3240,3258,3267,3268,3271,3277,3278,3286,3290,3291,3293,3294,3301,3302,3304,3305,3308,3310,3398,3405,3406,3410,3411,3412,3413,3414,3415,3416,3417,3418,3419,3420,3421,3422,3423,3424,3425,3426,3427,3428,3429,3430,3431,3432,3433,3434,3435,3436,3437,3442,3443,3444,3445,3446,3447,3448,3449,3451,3455,3456,3457,3458,3463,3465,3466,3474,3476,3484,3493,3523,3529,3530,3531,3533,3543,3578,3585,3597,3602,3606,3608,3614,3616,3617,3630,3638,3639,3642,3651,3673,3697,3706,3710,3713,3714,3717,3718,3719,3721,3723,3745,3746,3754,3761,3771,3772,3791,3800,3830,3838,3860,3865,3871,3879,3883,3894,3895,3897,3905,3925,3927,3929,3931,3932,3934,3947,3950,3954,3955,3962,3967,3971,3992,4003,4050,4087,4325,4384,4410,4424,4441,4448,4472,4502,4511,4518,4529,4646,4665,4693,4697,4781,4922,5334,5406,6163,6182,6261,6416,6688,7290,7330,7740,7741,7910,8203,8208,8242,8253,8453,8457,8510,8635,9117,9138,9661,9789,9844,9859,9922'

	#final_net[502]
	#[[731, 2751, []], [284, 499, []], [231, 315, []], [199, 581, []], [192, 500, []], ..... [3, 256, []], [3, 234, []], [3, 221, []]]
	#len(final_net[502]) #608

	#!!! filtered_most_associated == final_net[502]   #TRUE

	#!!! AND near_entities_seen == [f[1] for f in filtered_most_associated]   #TRUE

	tot = 0
	for f in final_net:
	    tot = tot + len(final_net[f])
	    
	if single_debug:
		printflush("##TOTAL NUMBER OF EDGES: "+str(tot))    #2145
		printflush("#EDGES AROUND GARNET ALONE: "+str(len(final_net[goid])))  #  352
		
	#near_entities_seen[0]        #2751
	#filtered_most_associated[0]  #[731, 2751, []]

	sm_jo, text_ids_needed_for_demo  = construct_small_json(near_entities_seen,filtered_most_associated,center_entity)

	gsmall_net = time.clock()
	printflush("\nIMPORTANT TIME INFO, Small Network took : "+str((gsmall_net - gmake_net)/60)+" minutes")
	#print sm_jo
	printflush("**********************************************************\n\n")
	printflush("Small Nodes: "+str(len(sm_jo['elements']['nodes'])))  #357
	printflush("Small Edges: "+str(len(sm_jo['elements']['links'])))  #352 
	printflush("Small Text Snippets: "+str(len(text_ids_needed_for_demo))) #3688


	#HANDLE SMALL CASE
	#-----------------------------------------------------------------------------------------

	#nodes_sorted_by_id = sorted(sm_jo['elements']['nodes'], key=lambda k: k['data']['id']) 
	#for i,e in enumerate(nodes_sorted_by_id):
	#    if i < 13:
	#        print str(i)+": "+ str(e['data']['id'])+' , '+e['data']['full_name']

	#D3 wants the source and target values to match the numbered index of the nodes
	#so we need to make a map of our node entity id's to their index ids, 
	#print nodes_sorted_by_id  .. nodes found in nodes


	#print sm_jo['elements']['edges']
	sm_jocopy = copy.deepcopy(sm_jo)

	#1.  only include nodes which are definitely linked to!!  
	all_link_nodes = []
	for i, e in enumerate(sm_jo['elements']['links']):
	    if e['source'] not in all_link_nodes:
		if single_debug:
			printflush("ADD source: "+str(e['source']))
		all_link_nodes.append(e['source'])
		
	    if e['target'] not in all_link_nodes:
		if single_debug: 
			printflush("ADD target: "+str(e['target']))
		all_link_nodes.append(e['target'])

	if single_debug:
		print len(all_link_nodes)  #353 if this is working correctly!


	#2.  remove nodes not in all_link_nodes
	newnodes = []
	for i,n in enumerate(sm_jo['elements']['nodes']):
	    if n['id'] in all_link_nodes:
		newnodes.append(n)
	    else:
		if single_debug:
			printflush(str(i)+": didn't find the following in all_link_nodes: "+str(n['id'])+" so remove it")
		

	if single_debug:
		printflush("nnodes: ",len(newnodes))  #there should be no "didn't find messages!"


	#3.  make dict from entid to nodes index id
	entid_to_node = {}
	index_to_endit = {}
	for i,n in enumerate(newnodes):
	    entid_to_node[n['id']] = i
	    index_to_endit[i] = n['id']


	#print index_to_endit[entid_to_node[496]]


	#4.  and then change all links to use them!
	newlinks = copy.deepcopy(sm_jo['elements']['links'])
	for i,e in enumerate(newlinks):
	    e['source'] = entid_to_node[e['source']]
	    e['target'] = entid_to_node[e['target']]

	#newlinks[0]

	#5.  change sm to use new nodes and new links
	sm_jo["elements"]["nodes"] = newnodes
	sm_jo["elements"]["links"] = newlinks


	#check url_list for urls json if needed
	#url_list  #if this is undefined, run generate_url_list function below!
	
	#make url list indexed by mongoid so that edges just need mongoid to show id
	#CORRECTION JUST USE IT AS THE INTEGER of its position in mongoid... maybe

	#if single_debug:
	#	printflush("ZZZZ CURRENT URL LIST before")
	#	print url_list

	'''
	if 'url_list' in globals():
		if url_list == {}:
			url_list = generate_url_list()
	else:	
		url_list = generate_url_list()
	'''
	url_list = generate_url_list()

	printflush("Now Save files")
	if single_debug:
		printflush("ZZZZ CURRENT URL LIST AFTER")
		#print url_list
	
	for i,n in enumerate(newnodes):
		if single_debug:
			try:
				printflush( str(i)+": "+n["full_name"]+"("+str(n['id'])+")")
			except:
				printflush("error printing node name")

	 
	if single_debug:
		#print sm_jo
		gsmall_net_end = time.clock()
		printflush("\nIMPORTANT TIME INFORMATION: massaging smallnet into what d3 wants took "+str(gsmall_net_end - gsmall_net)+" seconds")


	#1) save REVISED small json file  
	small_json_file = saved_jsons_path +"/"+ center_entity.lower().replace(" ","_") +"-smallnet-" + time.strftime("%m-%d_%I-%M-%S") + ".json"
	small_json_html = htmlpath +"/"+ center_entity.lower().replace(" ","_") +"-smallnet-" + time.strftime("%m-%d_%I-%M-%S") + ".json"
	with open(small_json_file, 'wb') as fp:
	    json.dump(sm_jo, fp)

	#2) save small text snippets file
	#if single_debug:
	#	printflush(text_ids_needed_for_demo)  #list of ids

	textjson = {}
	for t in text_ids_needed_for_demo:
	    textjson[t] = text_snippets[t]

	text_snippets_file = saved_jsons_path +"/"+ center_entity.lower().replace(" ","_") +"-textsnippets-" + time.strftime("%m-%d_%I-%M-%S") + ".json"
	text_snippets_html = htmlpath +"/"+ center_entity.lower().replace(" ","_") +"-textsnippets-" + time.strftime("%m-%d_%I-%M-%S") + ".json"
	with open(text_snippets_file, 'wb') as fp:
	    json.dump(textjson, fp)

	#3) write mongo - url dict
	small_urls_file = saved_jsons_path + "/"+ center_entity.lower().replace(" ","_") +"-small-urls-" + time.strftime("%m-%d_%I-%M-%S") + ".json"
	small_urls_html = htmlpath + "/"+ center_entity.lower().replace(" ","_") +"-small-urls-" + time.strftime("%m-%d_%I-%M-%S") + ".json"
	with open(small_urls_file, 'wb') as fp:
	    json.dump(url_list, fp)


	#COPY THESE FILES DIRECTLY OVER TO (../whoyouelect-april27/data/)
	printflush("\nDone saving small network files: "+small_json_file+" , "+text_snippets_file +", and "+small_urls_file)
	printflush("\nNow copy them over to webspace:")
	copyfile(small_json_file,small_json_html)
	copyfile(text_snippets_file,text_snippets_html)
	copyfile(small_urls_file,small_urls_html)	

	
	#NOW HANDLE LARGER CASE
	if also_larger == True:
		#lg_jo, lg_texts_needed = construct_large_json(one_out_nodes,final_net,center_entity)
		#lg_jo, lg_texts_needed = construct_large_json_take2(sm_jocopy, final_net,center_entity)
		printflush("NOW BEGIN CONSTRUCTION OF LARGE NET")
		glnet_start = time.clock()
		lg_jo, lg_texts_needed = construct_large_json_take3(sm_jocopy, final_net,center_entity, larger_relations,debug)
		printflush("LARGER Nodes: "+str(len(lg_jo['elements']['nodes'])))  #798
		printflush("LARGER Edges: "+str(len(lg_jo['elements']['links'])))  #5573 
		printflush("LARGER Text Snippets: "+str(len(lg_texts_needed))) #9128
		glnet_end = time.clock()
		printflush("IMPORTANT TIME INFO, LARGE Network took : "+str((glnet_end - glnet_start)/60)+" minutes")

		 

		#1) save large json file  (TODO:  maybe get rid of mongoid stuff)
		large_json_file = saved_jsons_path + "/"+ center_entity.lower().replace(" ","_")+"-largenet-" + time.strftime("%m-%d_%I-%M-%S") + ".json"
		large_json_html = htmlpath + "/"+ center_entity.lower().replace(" ","_")+"-largenet-" + time.strftime("%m-%d_%I-%M-%S") + ".json"
		with open(large_json_file, 'wb') as fp:
		    json.dump(lg_jo, fp)

		#2) save small text snippets file
		#printflush(lg_texts_needed)  list of ids
		largetextjson = {}
		for t in lg_texts_needed:
		    largetextjson[t] = text_snippets[t]

		large_text_snippets_file = saved_jsons_path + "/"+ center_entity.lower().replace(" ","_") +"-textsnippets-large-" + time.strftime("%m-%d_%I-%M-%S") + ".json"
		large_text_snippets_html = htmlpath + "/"+ center_entity.lower().replace(" ","_") +"-textsnippets-large-" + time.strftime("%m-%d_%I-%M-%S") + ".json"
		with open(large_text_snippets_file, 'wb') as fp:
		    json.dump(largetextjson, fp)

		printflush("\nDone saving large network files: "+large_json_file+" , and "+large_text_snippets_file)
		printflush("\nNow copy them over to webspace: "+large_json_html+" and "+large_text_snippets_html)
		copyfile(large_json_file,large_json_html)
		copyfile(large_text_snippets_file,large_text_snippets_html)


	#NOW HANDLE REWRITE OF CONFIG FILE
	printflush("Rewrite config file")
	with open(save_config_file) as json_data:
		configjson = json.load(json_data)
		sjh = small_json_html.split("/")[-1]
		suh = small_urls_html.split("/")[-1]
		tsh = text_snippets_html.split("/")[-1]
		if also_larger:
			ljh = large_json_html.split("/")[-1]
			lth = large_text_snippets_html.split("/")[-1] 

		if center_entity in configjson:
			pr = configjson[center_entity]
			if also_larger:
				#rewrite everything with the 5 new files
				configjson[center_entity] = [sjh, suh, tsh, ljh, lth]
			else:	
				#just rewrite small json files and leave 2 old large as they were
				configjson[center_entity] = [sjh, suh, tsh, pr[3],pr[4]]
		else:
			pr = ""
			if also_larger:
				#write all into new index
				configjson[center_entity] = [sjh, suh, tsh, ljh, lth]
			else:
				#write small into new index and default large ones to ""
				configjson[center_entity] = [sjh, suh, tsh, "", ""]
	
	#skip making backup for now
	#make backup and then save
	#copyfile(save_config_file,save_config_file+".bak"+time.strftime("%m-%d_%I-%M-%S"))
	
	with open(save_config_file, 'wb') as fp:
	    json.dump(configjson, fp)


	#add wiki content to people
	#"wiki_stub" #url
	
	

	#if photo_url for center_entity is null, find prior center_entity photo_url if any, and if so reuse it ( so you don't have to keep changing that! )
	#prior_small_net = pr[0]
	if pr != "":
		#with open("data/jsons/"+pr[0]) as psmn:
		with open(basep + "/whoyouelect/whoyouelect.com/texas/data/"+pr[0]) as psmn:  #use html version though this should be identical to data backend version
			prior_small_net = json.load(psmn)
			ns = prior_small_net["elements"]["nodes"]
			printflush("Prior Json: "+pr[0])
			printflush("#nodes = "+str(len(ns)))

			centercurrentphoto = "";
			centercurrentwiki = "";
			centerid = -1
			for n in ns:
				entity = n['full_name']
				found,currentphoto,currentwiki,sm_jo = handle_photos(entity,ns,sm_jo,debug)
				if entity == center_entity:
					centercurrentphoto = currentphoto
					centercurrentwiki = currentwiki
					centerid = found
			
			printflush("Success in using prior photo url: Save updates to Small Json File and copy to Html Folder after")
			#save update and copy to webspace
			with open(small_json_file, 'wb') as fp:
			    json.dump(sm_jo, fp)
			copyfile(small_json_file,small_json_html)
	else:
		printflush("Handlephotos for entities with no priors!!")  #HERE NOW (need to add Abel to config file as well)
		for i,n in enumerate(sm_jo["elements"]["nodes"]):
			entity = n['full_name']
			wiki_url = get_wiki_link(entity)
			if wiki_url == "":
				n["wiki_stub"] = "no wiki page"
			else:
				n["wiki_stub"] = wiki_url

			if "photo_url" not in n and n["wiki_stub"] != "no wiki page" and n["wiki_stub"] != "":
				wikistub = wiki_url.split("/")[-1]
				n["photo_url"] = get_wiki_photo(wikistub)

			if entity == center_entity:
				try:
					centercurrentphoto = n["photo_url"]
				except:
					print "ERROR with getting center currentphoto"
					centercurrentphoto = ""

				centercurrentwiki = n["wiki_stub"]
				centerid = i
				


	#HERE : fill in seperate description json config file ( js / configdesc.json ) 
	with open(save_configdesc_file) as jdata:
		cdescjson = json.load(jdata)

		#now, check to see if centery entity person already exists and is filled in
		info1 = ""
		info2 = ""
		if center_entity not in cdescjson:
			centerp = sm_jo["elements"]["nodes"][centerid]
			if centerp["full_name"] == center_entity:
				#just double checking name is right
				printflush("Constructing Config Description file for "+center_entity)
				printflush("Found entity = ")
				printflush( centerp)

				try:
					snippet = ""
					if "wiki_stub" in centerp:
						if centerp["wiki_stub"] != "" and centerp["wiki_stub"] != "no wiki page":
							wikistub = centercurrentwiki.split("/")[-1]
							snippet = get_wiki_shortbio(wikistub)
							if snippet != "" and len(snippet) == 2:
								snippet = snippet[0]

					showmap = 0
					if "district" in centerp:
						showmap = 1;
						if "chamber" not in centerp:
							if "position" in centerp:
								if centerp["position"] == "Representative":
									centerp["chamber"] = "lower"
								else:	
									centerp["chamber"] = "upper"
						info2 = "District: "+ str(centerp["district"])

					if "level" not in centerp:
						print("Error:  level not in centerp so set default one! Fix in configdesc.json ")
						centerp["level"] = "statewide-active"
					
					if 'position' in centerp:
						if type(centerp['position']) == list:
							centerp['position'] = " ".join(centerp['position']) 
		
					key = {"statewide-active":"State", "federal-active":"Federal", "statewide-active-elected":"","statewide-inactive":"Former State","statewide-active elected":""}
					if "party" in centerp and "position" in centerp:
						info1 = centerp["party"] + " " + key[centerp["level"]] + " " + centerp["position"] 
					elif "position" in centerp:
						info1 = key[centerp["level"]] + " " + centerp["position"] 
					elif "party" in centerp: 
						info1 = centerp["party"] + " " + key[centerp["level"]]    #found statewide-inactive!! 
						if centerp["level"] == "statewide-inactive":
							printflush("ERROR: FOUND statewide-inactive for center entity")
							printflush(centerp)
					else:
						printflush("Didn't find info1 data to use!")
						info1 = ""
				except:
					traceback.print_exc(file=sys.stdout)
					print("Setting configdesc.json values to NULL so fix this by hand!!")
					if 'info1' not in locals(): info1 = ""
					if 'info2' not in locals(): info2 = ""
					if 'centercurrentphoto' not in locals(): centercurrentphoto = ""
					if 'snippet' not in locals(): snippet = ""
					if 'showmap' not in locals(): showmap = 0


				cdescjson[center_entity] = {"info1":info1,"info2":info2, "image":centercurrentphoto, "snippet":snippet, "showmap":showmap}	
		
		#else leave it as it is
		
		with open(save_configdesc_file, 'wb') as fp:
		    json.dump(cdescjson, fp)


	#add photos/wikis to metadata db for quicker lookup
	gnodes_start = time.clock()
	handle_nodes_for_net(sm_jo,center_entity,debug)
	gnodes_end = time.clock()
	printflush("IMPORTANT TIME INFO.. handle_nodes took "+str((gnodes_end - gnodes_start))+" seconds total")
	
	gsn_end = time.clock()
	printflush("FINALLY DONE: Elapsed:  Generate File took "+str((gsn_end - gsn_start))+" seconds total")
	#TODO:FUTURE get 2nd image from google search with selenium for all PERSON entities who don't have "photourl"
	#TODO use context for a person ( Al Green ) when verifying them in articles found! XXX this only helps with out of state sources pretty much
	'''
	https://www.google.com/search?q=Bob+Libal&hl=ca&biw=1440&bih=778&site=imghp&tbs=isz:ex,iszw:200,iszh:200&tbm=isch&source=lnt
	img = document.querySelectorAll("ol#rso img")[1]
	click()
	document.querySelectorAll("img.irc_mi")[2].getAttribute("src")
	'''
	


if __name__ == '__main__':
	searchfor = sys.argv[1]
	also_larger = sys.argv[2]
	if also_larger == "include_larger" or also_larger == "also_larger":
		also_larger = True
	else:
		also_larger = False
	if len(sys.argv) > 3:
		debug = True      #if any third arg present set debug 
	else:
		debug = False

	load_from_file = True
	#python generate_single_network.py "Kyle Janek"     		   #generates small network only
	#python generate_single_network.py "Kyle Janek" include_larger     #generates both small and medium networks
	r = generate_single_network(also_larger,searchfor,debug,load_from_file)  #1st arg generates larger network or , and last says load from pickle file or not
