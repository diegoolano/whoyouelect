import csv
import sys
import os
import time

def start_searching(action,fname):
	with open(fname, 'rb') as f:
	    reader = csv.reader(f)
	    list_of_entities = list(reader)

	#print list_of_entities
	
	path = "/Users/dolano/htdocs/dama-larca/d3/generate_network/data/"
	for ent_details in list_of_entities:

		if len(ent_details) == 4:
			entname, level, title, party = ent_details
		elif len(ent_details) == 5:
			entname, level, title1, title2, party = ent_details
		else:
			print "ERRROR WITH LINE that is poorly formatted: "
			print ent_details
			sys.exit()			

		sds = ['austinamericanstatesman','dallasnewssearch','houstonchronsearch','nytimes','txobserver','txtribune']
		
		entname = entname.strip()
		entity = entname.replace(" ","_").replace("'","\'")
		print "\nPassed in "+entname
		print "\nChecking if folders for: "+entity+" already exist"
		found = 0
		need = []
		for s in sds:
			curpath = path+s+'/'+entity
			if os.path.isdir(curpath):
				print "--Path: "+curpath+" exists!"
			else:
				print "--Path: "+curpath+" doesn't exist!"
				need.append(s)
		

		if len(need) == len(sds) or action == "overwrite":			
			if "'" in entname:
				command = 'python do_websearch_for.py "' + entname +'" > debug_and_backup_files/'+entity+"-do_websearch_for-"+time.strftime("%m-%d_%I-%M-%S") + ".debug"
			else:
				command = "python do_websearch_for.py '" + entname +"' > debug_and_backup_files/"+entity+"-do_websearch_for-"+time.strftime("%m-%d_%I-%M-%S") + ".debug"
			print "UNIX CALL: "+command
			os.system(command)
			sleeptime = len(sds) * 3 #wait x seconds a source for calling and processing so your machine doesn't explode :)
			time.sleep(sleeptime)   
		elif len(need) == 0:
			if action == "overwrite":
				if "'" in entname:
					command = 'python do_websearch_for.py "' + entname +'" > debug_and_backup_files/'+entity+"-do_websearch_for-"+time.strftime("%m-%d_%I-%M-%S") + ".debug"
				else:
					command = "python do_websearch_for.py '" + entname +"' > debug_and_backup_files/"+entity+"-do_websearch_for-"+time.strftime("%m-%d_%I-%M-%S") + ".debug"
				print "ovewrite passed in so UNIX CALL: "+command
				os.system(command)
				sleeptime = len(sds) * 3  #wait x seconds a source for calling and processing so your machine doesn't explode :)
				time.sleep(sleeptime)
			else:
				print "Found folder in all sources and force overwrite not set so do nothing!"
		else:
			for n in need:
				if "'" in entname:
					command = 'python do_websearch_for.py "' + entname + '" notfull '+n+" > debug_and_backup_files/"+entity+"-do_websearch_for-source-"+n+"_"+time.strftime("%m-%d_%I-%M-%S") + ".debug"
				else:
					command = "python do_websearch_for.py '" + entname +"' notfull "+n+" > debug_and_backup_files/"+entity+"-do_websearch_for-source-"+n+"_"+time.strftime("%m-%d_%I-%M-%S") + ".debug"
				print "UNIX CALL: "+command
				os.system(command)
				time.sleep(8)  #wait x seconds a source
				
		print "\n"



if __name__ == '__main__':
	if len(sys.argv) > 1:
		action = sys.argv[1]
		if action == "confirm":
			if len(sys.argv) > 2:
				action = sys.argv[2]
			else:
				action = "don't overwrite"
			if len(sys.argv) > 3:
				fname = sys.argv[3]
			else:
				fname = 'entitiesoutput-tail3.csv'
			r = start_searching(action,fname)
		else:
			print("Error: Must Call Script with 'confirm' as an argument to run it")
	else:
		print("Error: Must Call Script with 'confirm' as an argument to run it")
