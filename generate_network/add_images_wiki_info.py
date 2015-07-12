from dama_globals import *
from dama_utils import *   #for db
import time
import json
import sys
import pickle
import copy
from dama_utils import *
import tarfile
import os.path
import os
from shutil import copyfile, move
import traceback
from wiki_funcs import *

basep = "/Users/dolano/htdocs/dama-larca/d3/"    #BASE PATH 
datap = basep + "generate_network/"
saved_jsons_path = datap + "data/jsons"
htmlpath = basep + "whoyouelect/whoyouelect.com/texas/data/"
save_config_file = basep + "whoyouelect/whoyouelect.com/texas/js/config.json"
save_configdesc_file = basep + "whoyouelect/whoyouelect.com/texas/js/configdesc.json"


def handle_photos(entity,ns,sm_jo):
	currentphoto = "";
	currentwiki = "";
	found = -1
	try:
		print("Looking up prior values for "+entity)
		prior_photo_url = "";
		prior_wiki_url = "";
		for n in ns:
			if n["full_name"] == entity:
				print("Found")
				print n
				if "photo_url" in n:
					prior_photo_url = n["photo_url"]
				else:
					print("No prior photo found so use blue dot!")

				if "wiki_stub" in n:
					prior_wiki_url = n["wiki_stub"]
				else:
					prior_wiki_url = get_wiki_link(entity)
				
				if prior_photo_url == "":
					if prior_wiki_url != "":
						#get stub
						wikistub = prior_wiki_url.split("/")[-1]
						prior_photo_url = '' #get_wiki_photo(wikistub)
					else:
						prior_photo_url = "images/bluedot.png";
 
				break

		print("Prior Photo URL: "+prior_photo_url)
		if prior_photo_url != "":
			for i,no in enumerate(sm_jo["elements"]["nodes"]):
				if no["full_name"] == entity:
					if "photo_url" not in no:      #only rewrite it if it doesn't have one
						print("Assign "+no["full_name"]+" photourl")
						sm_jo["elements"]["nodes"][i]["photo_url"] = prior_photo_url
						currentphoto = prior_photo_url
						found = i
						break
					else:
						currentphoto = no["photo_url"]
				
					if "wiki_stub" not in no:
						if prior_wiki_url != "":
							sm_jo["elements"]["nodes"][i]["wiki_stub"] = prior_wiki_url
						currentwiki = prior_wiki_url
					else:
						currentwiki = no["wiki_stub"]
		
	except:
		print("Warning: Couldn't complete prior photourl/prior wiki_url for "+entity)
		traceback.print_exc(file=sys.stdout)

	return [found,currentphoto,currentwiki,sm_jo]


def add_info(center_entity):

	with open(save_config_file) as json_data:
		configjson = json.load(json_data)
		pr = configjson[center_entity]

		#if photo_url for center_entity is null, find prior center_entity photo_url if any, and if so reuse it ( so you don't have to keep changing that! )
		#prior_small_net = pr[0]
		
		with open("data/jsons/"+pr[0]) as psmn:
			prior_small_net = json.load(psmn)
			ns = prior_small_net["elements"]["nodes"]
			print("Prior Json: "+pr[0])
			print("#nodes = "+str(len(ns)))

			centercurrentphoto = "";
			centercurrentwiki = "";
			centerid = -1
			for n in ns:
				entity = n['full_name']
				found,currentphoto,currentwiki,sm_jo = handle_photos(entity,ns,sm_jo)
				if entity == center_entity:
					centercurrentphoto = currentphoto
					centercurrentwiki = currentwiki
					centerid = found
			
			print("Success in using prior photo url")
			#save update and copy to webspace
			with open(small_json_file, 'wb') as fp:
			    json.dump(sm_jo, fp)
			copyfile(small_json_file,small_json_html)


if __name__ == '__main__':
	searchfor = sys.argv[1]
	r = add_info(searchfor)
