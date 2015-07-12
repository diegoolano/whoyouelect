from dama_globals import *
from dama_utils import *   #for db
import time
import json
import sys
import tarfile
import os.path
import os
import traceback
import time

basep = "/Users/dolano/htdocs/dama-larca/d3/"    #BASE PATH TO CHANGE
save_config_file = basep + "/whoyouelect/whoyouelect.com/texas/js/config.json"
save_network_path = basep + "/whoyouelect/whoyouelect.com/texas/data/"

def handle_nodes_for_net(smm,center_entity,debug=False):
	
	e = center_entity
	conn = MongoClient()
	db = conn.newsdb
	#db.texnews.wikiandphotos
	for s in smm["elements"]["nodes"]:
		foundphoto = 0
		foundwiki = 0
		photo = ""
		wiki = ""
		#look if s has a non empty photo_url or wiki_stub
		if 'photo_url' in s:
			if s['photo_url'] != "":
				photo = s['photo_url']
				foundphoto = 1;

		if 'wiki_stub' in s:
			if s['wiki_stub'] != "" and s['wiki_stub'] != "no wiki page":
				wiki = s['wiki_stub']
				if debug: print("XXXXX FOUND WIKI STUB "+wiki)
				foundwiki = 1

		if foundphoto == 1 or foundwiki == 1:
			if debug: print("FOUND THAT "+s["full_name"]+" has a photo_url or wiki_stub set so now check in DB")
			#time.sleep(1)
			rr = db.texnews.wikiandphotos.find({"full_name" : s['full_name']})
			if rr.count() == 1:
				if debug: print "Rcount == 1"
				for r in rr:
					#if it already exits don't touch it ( but maybe keep an ongoing counter of how many times we've seen this person with in json
					if 'found_in_network' in r:
						if debug: print("UPDATE: Add that small node "+s['full_name']+" was found in nodes file for "+e+" to its row in DB")
						fin = r['found_in_network']
						if debug: 
							print("also found in")
							print(fin)
						if fin == None:
							if debug: print("ERROR Why was fin empty!!")
							fin = [e]
						else:
							fin.append(e)

						if debug:
							print("post fin")
							print(fin)

						if foundwiki == 1 and ( r['wiki_stub'] == "" or  r['wiki_stub'] == "no wiki page"):
							db.texnews.wikiandphotos.update({"full_name":s['full_name']},{"$set": {"found_in_network":fin, "wiki_stub":wiki, 'photo_url':r['photo_url'] }})
						elif foundphoto == 1 and r['photo_url'] == "":
							db.texnews.wikiandphotos.update({"full_name":s['full_name']},{"$set": {"found_in_network":fin, "wiki_stub":r['wiki_stub'], 'photo_url': photo }})
						else:
							db.texnews.wikiandphotos.update({"full_name":s['full_name']},{"$set": {"found_in_network":fin, "wiki_stub":r['wiki_stub'], 'photo_url':r['photo_url']}})
					else:
						if debug:
							print "ERROR: not found_in_network"
							print r
			else:
				toadd = {'full_name':s['full_name'], 'photo_url':photo, 'wiki_stub':wiki, 'found_in_network':[e]}
				if debug:
					print "Rcount != 1... It equals "+str(rr.count())
					print("ADD NEW NODE to db: ")
					print(toadd)
				rr = db.texnews.wikiandphotos.find({"full_name" : s['full_name']})
				if rr.count() == 0:
					if debug: print "Couldnt' find fullname:"+s['full_name']+" in DB twice so add it ! "
					#db.texnews.wikiandphotos.insert(toadd)  #--- hmmm do this after
				else:
					if debug: print "TODO: This time we found it so handle this ! "
				
					
	#NO NEED since the smll and largenet nodes should be the same!  print "CURRENTLY LOOKING AT LARGE NODES FOR "+e+" ["+medium+"]"

def go_through_small_medium_config_jsons_and_add_wikiurl_and_photorul_to_mongo():
	
	with open(save_config_file) as json_data:
		configjson = json.load(json_data)
		#configjson[center_entity] = [sjh, suh, tsh, ljh, lth]
		for e in configjson:
			ce = configjson[e]   #e is the center entity for that file, whereas ce is its configuration
			small = ce[0]
			medium = ce[3]
			print "CURRENTLY LOOKING AT SMALL NODES FOR "+e+" - "+small+""
			
			#HERE ACTUALLY LOAD FILE
			with open(save_network_path + small) as smalljson:
				smm = json.load(smalljson)
				handle_nodes_for_net(smm,True)
	

if __name__ == '__main__':
	go = sys.argv[1]
	if go == "go":
		r = go_through_small_medium_config_jsons_and_add_wikiurl_and_photorul_to_mongo()
