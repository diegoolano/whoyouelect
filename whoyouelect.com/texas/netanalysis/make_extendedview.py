import os, sys,traceback
import json, time
from shrink_large import *
from make_large_node_article_map  import *

def make_extendedview(f):
	print("Making Extended View From "+f)

	#make articlemap
	curd = startmap(f)  

	#make ncol and nodes files
	startncol(f,curd,True)   #pass in true so that starnocl knows to load from json object instead of loading it again

	print("Done")
if __name__ == '__main__':
	f = ""
	if len(sys.argv) > 1:
		f = sys.argv[1]
		make_extendedview(f)
