import sys
import shutil
import os

def delete_entity(entity,only_source):
	print "DELTE FOLDERS/FILES FOR "+entity
	entity = entity.replace(" ","_").replace("'","\'")
	path = "/Users/dolano/htdocs/dama-larca/d3/generate_network/data/"
	if only_source == False:
		sds = ['austinamericanstatesman','dallasnewssearch','houstonchronsearch','nytimes','txobserver','txtribune']
		
		for s in sds:
			if os.path.isdir(path+s+'/'+entity):
				shutil.rmtree(path+s+'/'+entity)    

			#now look for bogies
			if os.path.isdir(path+s+'/'):
				for d in os.listdir(path+s+'/'):
					if entity in d:
						print("Found "+entity+" in "+s+'/'+d+' so delete it')
						shutil.rmtree(path+s+'/'+d)
			else:
				print("Didn't find path: "+path+s+'/')
	else:
		print "ONLY DELETE FOR SOURCE: "+only_source
		s = only_source
		if os.path.isdir(path+s+'/'+entity):
			shutil.rmtree(path+s+'/'+entity)    

		#now look for bogies
		if os.path.isdir(path+s+'/'):
			for d in os.listdir(path+s+'/'):
				if entity in d:
					print("Found "+entity+" in "+s+'/'+d+' so delete it')
					shutil.rmtree(path+s+'/'+d)
		else:
			print("Didn't find path: "+path+s+'/')
		
		
	if os.path.exists(path+'pickles/'+entity+'.pickle'):
		os.remove(path+'pickles/'+entity+".pickle")

	if os.path.exists(path+'pickles/'+entity+'.tar.gz'):
		os.remove(path+'pickles/'+entity+".tar.gz")
	
	if os.path.exists(path+'numbers/'+entity+".txt"):
		os.remove(path+'numbers/'+entity+".txt")


if __name__ == '__main__':
	ent = sys.argv[1].replace(" ","_")
	if len(sys.argv) > 2:
		only_source = sys.argv[2]
	else:
		only_source = False
	r = delete_entity(ent,only_source)	
