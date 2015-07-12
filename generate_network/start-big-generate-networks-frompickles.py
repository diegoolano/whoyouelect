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
			print "NOW CALLING generate_single_netork with "+searcharg
			command = "python generate_single_network.py '"+searcharg+"' include_larger  > debug_and_backup_files/"+searcharg.replace(" ","_")+"-generate_single_net-"+time.strftime("%m-%d_%I-%M-%S") + ".debug"
			print "\tUNIX FOREGROUND BLOCKING CALL: "+command
			os.system(command)
			print "************************************************************************************************"
		except:	
			print "ERRROR IN start_adding!"
			traceback.print_exc(file=sys.stdout)
	os.system("say -v diego 'The dishes are done man.'")


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
