import os, sys,traceback
import json, time
import gzip   #https://pythonadventures.wordpress.com/2015/01/07/opening-gzipped-json-files/

def shrink_edges(curd, debug=False):
    enttype_to_index = {'same sentence':'s','same article':'a','near':'n'}

    for ind,l in enumerate(curd['elements']['links']):
	try:
		thisinst = {'s':0, 'a':0, 'n': 0}
		for f in l['inst']:
			thisinst[enttype_to_index[f['type']]] += 1	
		
		curd['elements']['links'][ind]['inst'] = thisinst
	except:
	    print ind, l
	    traceback.print_exc(file=sys.stdout)
	    sys.exit()
    return curd


def removefile(f):
	print("REMOVE ORIGINAL FILE: "+f)
	os.remove(f)
    
def save_shrinked(f,curd):
    #f is the file name
    nodesf = f+".nodes"
    edgesf = f+".edges"

    with open(f,'wb') as me:
    	json.dump(curd, me)
        os.system("sed 's/ //g' "+f+" > "+f+".nospace")
        os.system("sed 's/inst/i/g' "+f+".nospace > "+f+".new")
	os.system("rm "+f+".nospace")
        os.system("sed 's/source/s/g' "+f+".new > "+f+".src")
	os.system("rm "+f+".new")
        os.system("sed 's/target/t/g' "+f+".src > "+f+".new")
	os.system("rm "+f+".src")

    ''' #splitting doesn't actually help save space much.. almost everything is in edges
    with open(nodesf,'wb') as me:
    	json.dump(curd['elements']['nodes'], me)
        os.system("sed 's/ //g' "+nodesf+" > "+nodesf+".nospace")
        os.system("sed 's/inst/i/g' "+nodesf+".nospace > "+nodesf+".new")
	os.system("rm "+nodesf+".nospace")

   
    with open(edgesf,'wb') as me:
    	json.dump(curd['elements']['links'], me)
        os.system("sed 's/ //g' "+edgesf+" > "+edgesf+".nospace")
        os.system("sed 's/inst/i/g' "+edgesf+".nospace > "+edgesf+".new")
	os.system("rm "+edgesf+".nospace")
    '''

def remove_dupes(curd):
	seen = {}
	newlinks = []
	print "TOTAL NODES",len(curd['elements']['nodes'])
	print "TOTAL EDGES",len(curd['elements']['links'])

        for ind,l in enumerate(curd['elements']['links']):
		sr = l["source"]
		tr = l["target"]
		if sr in seen:
			if tr in seen[sr]:
				do_nothing = 1
			else:
				if tr in seen:
					if sr in seen[tr]:
						do_nothing = 1
					else:
						seen[sr][tr] = 1
						seen[tr][sr] = 1
						newlinks.append(l)		
				else:
					seen[sr][tr] = 1
					seen[tr] = {}
					seen[tr][sr] = 1
					newlinks.append(l)		
		else:
			if tr in seen:
				if sr in seen[tr]:
					do_nothing = 1
				else:
					seen[sr]  = {}
					seen[sr][tr] = 1
					seen[tr][sr] = 1
					newlinks.append(l)
			else:
				seen[sr] = {}
				seen[sr][tr] = 1
				seen[tr] = {}
				seen[tr][sr] = 1
				newlinks.append(l)

	curd['elements']['links'] = newlinks
	print "TOTAL EDGES AFTER DEDUPE",len(curd['elements']['links'])
	return curd

def calculate_metric(counts):
	totalinsts = counts['s'] + counts['n'] + counts['a']
	multiplier_numerator = totalinsts
	multiplier_denominator = counts["a"]
	if multiplier_denominator == 0: 
		multiplier_denominator = 1

	multiplier = multiplier_numerator / multiplier_denominator
	weight = multiplier * ( counts["s"]  +  (.5 * counts["n"] ) + (.1 * counts["a"] ) )
	return [weight,totalinsts]  


def make_ncol(curd,f):
	entname = f.split("-")[0]
	
	#id,id2,weight
	ncolout = ""
        for ind,l in enumerate(curd['elements']['links']):
		w,num = calculate_metric(l['inst'])
		ncolout += str(l['source']) + " " + str(l['target']) + " " + str(w) + " " + str(num) + "\n"

    	with open(entname+".ncol",'wb') as ncolfile:
    		ncolfile.write(ncolout)

	with open(entname+"-nodes.json",'wb') as me:
		json.dump(curd['elements']['nodes'], me)


	
def startncol(f,curd,object_passed_in=False):
	if object_passed_in == False:
		imst = time.clock()
		with open(f) as jdata:
			curd = json.load(jdata)
		imend = time.clock()
		print("--TIME INFO:  loading took "+str(imend - imst)+" seconds") 
	else:
		print("--TIME INFO:  JSON object passed in so no need to load from file again") 
		
	
	imst = time.clock()
	curd = remove_dupes(curd)
	imend = time.clock()
	print("--TIME INFO:  remove dupes took "+str(imend - imst)+" seconds") 

	imst = time.clock()
	curd = shrink_edges(curd)
	imend = time.clock()
	print("--TIME INFO:  shrink edges took "+str(imend - imst)+" seconds") 

	imst = time.clock()
	make_ncol(curd,f)
	imend = time.clock()
	print("--TIME INFO:  make ncol took "+str(imend - imst)+" seconds") 


	#imst = time.clock()
	#save_shrinked(f,curd)
	#imend = time.clock()
	#print("--TIME INFO:  saving took "+str(imend - imst)+" seconds") 
	
	#instead of saving optimized largenet which we won't use, just remove f since it already exists in tar file anyways
	removefile(f)
	


if __name__ == '__main__':
	f = ""
	if len(sys.argv) > 1:
		f = sys.argv[1]
		startncol(f,[],False)
