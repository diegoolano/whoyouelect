from concurrent import futures
#import urllib.request
#easy_install futures
import csv
import sys
import os
import traceback
import time

URLS = ['http://www.foxnews.com/',
        'http://www.cnn.com/',
        'http://europe.wsj.com/',
        'http://www.bbc.co.uk/',
        'http://some-made-up-domain.com/']

#def load_url(url, timeout):
#    return urllib.request.urlopen(url, timeout=timeout).read()

def check_dir(path_to_dir, attempts=0, timeout=10, sleep_int=5):
	if attempts < timeout:
		if os.path.exists(path_to_dir) and os.path.isfile(path_to_file): 
			return "Completed"
		else:
			# perform an action
			time.sleep(sleep_int)
			check_dir(path_to_dir, attempts + 1)
	else:
		return "Couldn't find "+check_dir+".  Its either still loading or there was an error"


def start_load(entname):
	n = "houstonchronsearch"
	#entity = entname.replace(" ","_")	
	entity = entname.replace(" ","_")
	command = 'python do_websearch_for.py "' + entname + '" notfull '+n+" > debug_and_backup_files/"+entity+"-do_websearch_for-source-"+n+"_"+time.strftime("%m-%d_%I-%M-%S") + ".debug &"
	print "UNIX CALL (in background): "+command
	os.system(command)
	entityfolder = "data/houstonchronsearch/"+entname.replace(" ","_")
	#return check_dir(entityfolder)
	

def redo_houston():
	#fname = "entitiesoutput.csv"
	#fname = "chron-redos.csv"
	#fname = "chron-redos2.csv"
	fname = "chron-redos3.csv"
	with open(fname, 'rb') as f:
	    reader = csv.reader(f)
	    list_of_entities = list(reader)

	people = [l[0].strip() for l in list_of_entities]
	print "Handle "+str(len(people))+" people"

	to_remove = []
	to_keep = []
	#bak up folders
	'''
	for i,p in enumerate(people):
		oldentityfolder = "data/houstonchronsearch/"+p.replace(" ","_")
		bakentityfolder = "data/houstonchronsearch/"+p.replace(" ","_")+"bak"
		#if os.path.exists(oldentityfolder):
		#	print "Rename" + oldentityfolder + " to "+ bakentityfolder
		#	os.rename( oldentityfolder, bakentityfolder )   #move from query with \"Rep_\"  to Allen_fisher
		#else:
		if os.path.exists(bakentityfolder):
			print("Found backup already "+bakentityfolder)
			to_keep.append(i)
		else:
			print("*****Didn't find backup for "+oldentityfolder+" , "+bakentityfolder)
			print("*****so manually handle: "+p+" at index: "+str(i))
			to_remove.append(i)
	
	newpeople = []
	#for ind in to_remove:
	#	del people[ind]

	for ind in to_keep:
		newpeople.append(people[ind])
	'''
	#print "After moving things, handle "+str(len(newpeople))+" people"
	print people

	
	for i,p in enumerate(people):
		print "HANDLING: "+p
		start_load(p)
		if i % 10 == 0:
			print "I: "+str(i)+" so sleep 2 minutes to let processes finish"
			time.sleep(120)
		
	'''
	with futures.ThreadPoolExecutor(max_workers=10) as executor:
	    future_to_url = dict((executor.submit(start_load, p), p)
				 for p in people)
	    #future_to_url = dict((executor.submit(load_url, url, 60), url) for url in URLS)

	    for future in futures.as_completed(future_to_url):
		p = future_to_url[future]
		if future.exception() is not None:
		    print('%r generated an exception: %s' % (p,
							     future.exception()))

		    print('%r returned %r' % (p, str(future.result())))

	'''

if __name__ == '__main__':
	if len(sys.argv) > 1:
		action = sys.argv[1]
		if action == "confirm":
			redo_houston()
		else:
			print("Error: Must Call Script with 'confirm' as an argument to run it")
	else:
		print("Error: Must Call Script with 'confirm' as an argument to run it")
