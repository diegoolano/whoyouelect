import sys
import shutil
import os
import json

basep = "/Users/dolano/htdocs/dama-larca/d3/"    #BASE PATH 
datap = basep + "generate_network/"
saved_jsons_path = datap + "data/jsons"
htmlpath = basep + "whoyouelect/whoyouelect.com/texas/data/"
save_config_file = basep + "whoyouelect/whoyouelect.com/texas/js/config.json"

#TODO MAKE THIS LOAD FROM CONFIGFILE in js/  
#AND THEN DELETE ONLY ONES FOR EXISTING ENTITIES THAT AREN'T THE CURRENT ONE
def clean_up_old_json():
	with open(save_config_file) as json_data:
		configjson = json.load(json_data)

	keep = []
	for e in configjson:
		for jf in configjson[e]:
			keep.append(jf)

	print keep
	#delete from generate_network/data/jsons
	for f in os.listdir(saved_jsons_path):
	    if f.endswith(".json"):
		if f not in keep:
			print "DELETE: "+f
			os.remove(saved_jsons_path+"/"+f)

	#delete from whoyouelect/data/
	for f in os.listdir(htmlpath):
	    if f.endswith(".json"):
		if f not in keep:
			print "DELETE: "+f
			os.remove(htmlpath+"/"+f)
	

	print "\nClean up done.  Now files in configfile are the only ones that are in data/jsons/"
	
if __name__ == '__main__':
	r = clean_up_old_json()	
