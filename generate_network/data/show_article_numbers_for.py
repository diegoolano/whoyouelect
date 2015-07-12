import sys
import os

def show_article_nums(searchfor):
	path = "/Users/dolano/htdocs/dama-larca/d3/generate_network/data/"
	searchfor = searchfor.replace(" ","_").replace("'","\\'")
	print("Showing Entity Article Numbers for folders: "+searchfor)
	ss = ["austinamericanstatesman","dallasnewssearch","houstonchronsearch","nytimes","txobserver","txtribune"]
	numfile = path + "numbers/"+searchfor+".txt"
	
	#remove prior results
	if os.path.exists(numfile):
		os.remove(numfile)

	#cycle through sources and add counts for each to numbers/entity.txt
	for s in ss:
		aa = path + s + "/"+searchfor
		if os.path.exists(aa+"/links-"+searchfor+".json"):
			os.system('echo "'+s+'" >> '+numfile+"; jq . "+aa+"/links-"+searchfor+'.json | grep "url" | wc -l >> '+ numfile)    #make this >> into numbers/searchforarticles.txt
		else:
			os.system('echo "'+s+' : no links file found so 0" >> '+numfile)
	
	if os.path.isfile(numfile):
		with open(numfile,'rb') as f:
			ff =  f.read()
			print ff
			f.close()
			

if __name__ == '__main__':
	searchfor = sys.argv[1].replace(" ","_")
	r = show_article_nums(searchfor)	
