import csv
import sys
import os
import time
import traceback

def start_adding(action,fname):
	with open(fname, 'rb') as f:
	    reader = csv.reader(f)
	    list_of_entities = list(reader)

	print "Number of Entities: "+str(len(list_of_entities))

	for searchterms in list_of_entities:
		try:
			searcharg = searchterms[0]
			print "************************************************************************************************"
			print "NOW CALLING add_json_files_for with "+searcharg
			command = "python add_json_files_for.py '" + searcharg +"' > debug_and_backup_files/"+searcharg.replace(" ","_")+"-addjson-"+time.strftime("%m-%d_%I-%M-%S") + ".debug" #with & it hits the shit out of the box so for now leave it in foreground
			print "\tUNIX FOREGROUND BLOCKING CALL: "+command
			os.system(command)
			print "************************************************************************************************"
		except:	
			print "ERRROR IN start_adding!"
			traceback.print_exc(file=sys.stdout)
	os.system("say -v diego 'Diego.. Diego.. Che.. Veni pelotudo.  Te necisito.'")


if __name__ == '__main__':
	if len(sys.argv) > 1:
		action = sys.argv[1]
		if action == "confirm":
			if len(sys.argv) > 2:
				fname = sys.argv[2]
			else:
				fname = 'entitiesoutput.csv'
			r = start_adding(action,fname)
		else:
			print("Error: Must Call Script with 'confirm' as an argument to run it")
	else:
		print("Error: Must Call Script with 'confirm' as an argument to run it")
