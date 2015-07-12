import os, sys,traceback
import json, time
import gzip   #https://pythonadventures.wordpress.com/2015/01/07/opening-gzipped-json-files/

'''
        "source": 595,
        "inst": [
          {
            "mongoid": "55559cb0dabb4fd417f69691",
            "textid": 18043,
            "type": "near"
          }
        ],
        "target": 59
      }

So we'll make a file that has a section which is the mongoid reference in the beginning.  a dict with a numeric id which maps to the mongoid which is long
then it will have a section which is indexed by nodeid and is an array of the articles that node appears in!

so go edge by edge and create that structure 


'''
def make_map(curd, debug=False):

    newstruct = {'ms': [], 'ns':{}}
    mongo_to_local = {}   #map from mongoid to its number id in newstruct['ms']
    nodekeys = []

    #print curd['elements'].keys()
    #sys.exit()

    for ind,l in enumerate(curd['elements']['links']):
	try:
		sr = l['source'];
		tr = l['target'];
		for f in l['inst']:
			#add mongo to list if we haven't seen it
			if f['mongoid'] not in newstruct['ms']:
				newstruct['ms'].append(f['mongoid'])
				mongo_to_local[f['mongoid']] = len(newstruct['ms'])

			#add sr to list if we haven't seen it, and add mongo local id to its array
			if sr not in nodekeys:
				newstruct['ns'][sr] = []
				newstruct['ns'][sr].append(mongo_to_local[f['mongoid']])
				nodekeys.append(sr)	
			else:
				#we have sr already in list, so now add mongoid if we don't have it 
				if mongo_to_local[f['mongoid']] not in newstruct['ns'][sr]:
					newstruct['ns'][sr].append(mongo_to_local[f['mongoid']])

			#now do same with target
			if tr not in nodekeys:
				newstruct['ns'][tr] = []
				newstruct['ns'][tr].append(mongo_to_local[f['mongoid']])
				nodekeys.append(tr)	
			else:
				if mongo_to_local[f['mongoid']] not in newstruct['ns'][tr]:
					newstruct['ns'][tr].append(mongo_to_local[f['mongoid']])
					
	except:
	    print ind, l
	    traceback.print_exc(file=sys.stdout)
	    sys.exit()
    return newstruct

    
def save_nodemap(f,curd):
    #f is the file name
    nodemapf = f.replace(".json","")+"-node-article-map.json"
    print("--SAVE TO FILE: "+nodemapf);

    with open(nodemapf,'wb') as me:    #save new map to oldfilename + -node-article-map.json
    	json.dump(curd, me)

	
def startmap(f):
	imst = time.clock()
	with open(f) as jdata:
		origcurd = json.load(jdata)
	imend = time.clock()
	print("--TIME INFO:  loading took "+str(imend - imst)+" seconds") 
	
	imst = time.clock()
	smallcurd = make_map(origcurd)
	imend = time.clock()
	print("--TIME INFO:  make_map took "+str(imend - imst)+" seconds") 

	imst = time.clock()
	save_nodemap(f,smallcurd)
	imend = time.clock()
	print("--TIME INFO:  saving took "+str(imend - imst)+" seconds") 
	
	return origcurd

if __name__ == '__main__':
	f = ""
	if len(sys.argv) > 1:
		#THIS EXPECTS AS INPUT A LARGENET FILE THAT HASN'T BEEN PROCESSED!!
		f = sys.argv[1]
		ogcurd = startmap(f)
