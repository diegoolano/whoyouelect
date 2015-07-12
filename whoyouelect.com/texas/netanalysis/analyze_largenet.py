import os, sys,traceback
import json, time
import gzip   #https://pythonadventures.wordpress.com/2015/01/07/opening-gzipped-json-files/


def count_edges_for_node(nid,curd):
	total = 0
	nid = int(nid)
	print "LOOKING UP id:", nid, " - ",curd['elements']['nodes'][nid]['full_name']
        for ind,l in enumerate(curd['elements']['links']):
		#w,num = calculate_metric(l['inst'])
		if l['source'] == nid or l['target'] == nid:
			srcname = curd['elements']['nodes'][l['source']]['full_name']
			tarname = curd['elements']['nodes'][l['target']]['full_name']
			print srcname," (",l['source'],") and ", tarname," (",l['target'],")",l
    			total += 1
	print "TOTAL",total
			


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


	
def start(f,nid):
	imst = time.clock()
	with open(f) as jdata:
		curd = json.load(jdata)
	imend = time.clock()
	print("--TIME INFO:  loading took "+str(imend - imst)+" seconds") 
	imst = time.clock()
	count_edges_for_node(nid,curd)
	imend = time.clock()
	print("--TIME INFO:  lookup took "+str(imend - imst)+" seconds") 


	

if __name__ == '__main__':
	f = sys.argv[1]
	nid = sys.argv[2]
	start(f,nid)
