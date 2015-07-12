import sys
import os

def show_source_summary(s):
	path = "/Users/dolano/htdocs/dama-larca/d3/generate_network/data/"
	print("Showing Source Summary for: "+s)
	ss = ["austinamericanstatesman","dallasnewssearch","houstonchronsearch","nytimes","txobserver","txtribune"]
	
	#cycle through sources and add counts for each to numbers/entity.txt
	if s in ss:
		aa = path + s + "/"
		dircontents = os.listdir(aa) 
		people = [ d for d in dircontents if '_' in d and '.py' not in d]		

		#print people
		os.system('echo "name,nonempty,empty" >> '+s+'.csv')
		for p in people:
			fullp = aa + p + "/"
			#os.system('echo "'+p+'" >> '+s+'.out')
			#os.system('find '+fullp+'*.json | xargs grep -lv \'"text": ""\' | wc -l >> '+s+'.out')    #number of nonempty articles
			#os.system('find '+fullp+'*.json | xargs grep -l \'"text": ""\' | wc -l >> '+s+'.out')    #number of empty articles

			os.system('echo "'+p+'," >> '+s+'.csv && find '+fullp+'*.json | xargs grep -lv \'"text": ""\' | wc -l >> '+s+'.csv && echo "," >> '+s+'.csv && find '+fullp+'*.json | xargs grep -l \'"text": ""\' | wc -l >> '+s+'.csv')    #number of empty articles

		#os.system('echo "'+s+'" >> '+numfile+"; jq . "+aa+"/links-"+searchfor+'.json | grep "url" | wc -l >> '+ numfile)    #make this >> into numbers/searchforarticles.txt
	
			

if __name__ == '__main__':
	searchfor = sys.argv[1]
	r = show_source_summary(searchfor)	
