import json
import sys
import os.path
import os
import traceback
from itertools import izip, islice, tee
from nltk.util import ngrams

def generate_ngrams(nodes,N):
	res = {}
	nodeids = {}
	for i,ent in enumerate(nodes):
		#print("\nFor "+ent["full_name"]+" "+str(N)+"grams: ")
		#{u'id': 498, u'full_name': u'Texas', u'entity_type': u'LOCATION'}   #TODO START TO USE entity_type
		ngrms = izip(*(islice(seq, index, None) for index, seq in enumerate(tee(ent["full_name"], N))))
		res[ent['full_name']] = list(ngrms)
		nodeids[ent['full_name']] = i
	
	return [res,nodeids]



#NOT TAKING INTO ACCOUNT TYPE
def compare_ngrams(nngrams,nodes,nodeids):
	threshhold = 0.8
	for n in nngrams:
		curn = nngrams[n]
		curn_len = len(curn)
		if curn_len == 0:
			print("SKIP entity: "+n+" which has length 0")
			continue

		curscores = {}
		#print "N: "+n
		#print curn
		#print "VS nltk"
		#generated_ngrams = list(ngrams(n, 3))   <--- can use in generate_ngrams if I want, but output of both is identical
		#print str(len(generated_ngrams))
		#print generated_ngrams
		#sys.exit()
		#Looking at Syracuse University
		#[(u'S', u'y', u'r', u'a'), (u'y', u'r', u'a', u'c'), (u'r', u'a', u'c', u'u'), (u'a', u'c', u'u', u's'), (u'c', u'u', u's', u'e'), 
		# (u'u', u's', u'e', u' '), (u's', u'e', u' ', u'U'), (u'e', u' ', u'U', u'n'), (u' ', u'U', u'n', u'i'), (u'U', u'n', u'i', u'v'), 
		# (u'n', u'i', u'v', u'e'), (u'i', u'v', u'e', u'r'), (u'v', u'e', u'r', u's'), (u'e', u'r', u's', u'i'), (u'r', u's', u'i', u't'), (u's', u'i', u't', u'y')]
		for o in nngrams:
			if o != n:
				othern = nngrams[o]
				curscores[o] = float(len(list(set(curn) & set(othern))))/curn_len
		highones = [ (c,curscores[c],nodes[nodeids[c]]['entity_type']) for c in curscores if curscores[c] > threshhold]
		if len(highones) > 0:
			print("For "+n+" ("+nodes[nodeids[n]]['entity_type']+")found possible merge candidates")
			print(highones)
			

def show_and_score_merges(searchforfile):
	try:
		with open(searchforfile) as json_data:
			net = json.load(json_data)
			nodes = net["elements"]["nodes"]
			print "Found "+str(len(nodes))+" nodes"
			ngrms,nodeids = generate_ngrams(nodes,3)
			rezo = compare_ngrams(ngrms,nodes,nodeids)

	except:
		print("Error:")
		traceback.print_exc(file=sys.stdout)
		

if __name__ == '__main__':
	searchfor = sys.argv[1]   # expecting  data/jsons/bob_libal-largenet... .json
	r = show_and_score_merges(searchfor)  
