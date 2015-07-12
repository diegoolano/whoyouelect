from dama_globals import *
import time
import json
import sys
import pickle
from dama_utils import *


saved_jsons_path = "/Users/dolano/htdocs/dama-larca/d3/generate_network/data/jsons"

def debug(center_entity):
    	global global_index     
	global entity_edges     
	global global_entities  
	global json_output      
	global text_snippets    
	global global_relations 

	with open('data/pickles/'+center_entity.replace(" ","_")+'.pickle','rb') as f:
		global_index, entity_edges, global_entities, center_entity, json_output, text_snippets, global_relations = pickle.load(f)
		
    	print "XXXXglobal_index (size:"+str(len(global_index))+")"     
    	print global_index     
	print "XXXXentity_edges (size:"+str(len(entity_edges))+")"     
	print entity_edges     
	print "XXXXglobal_entities (size:"+str(len(global_entities))+")"     
	print global_entities  
	print "XXXXjson_output (nodes:"+str(len(json_output['elements']['nodes']))+", edges: "+str(len(json_output['elements']['edges']))+")"  
	print json_output      
	print "XXXXtext_snippets (size:"+str(len(text_snippets))+")"    
	print text_snippets    
	print "XXXXglobal_relations (size:"+str(len(global_relations))+")" 
	print global_relations 
	

if __name__ == '__main__':
	#for debug purposes, do 
	#python debug_pickle.py "Bob Libal" > bobpickle.txt
	searchfor = sys.argv[1]
	r = debug(searchfor)  
