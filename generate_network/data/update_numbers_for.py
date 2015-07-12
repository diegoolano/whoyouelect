import sys
import os
from show_article_numbers_for import show_article_nums

def update_nums(searchfor):
	path = "/Users/dolano/htdocs/dama-larca/d3/generate_network/data/"
	numfile = path + searchfor
	content = []
	if os.path.exists(numfile):
		with open(numfile) as f:
    			content = f.readlines()

	peeps = [c.strip() for c in content]
	for p in peeps:
		show_article_nums(p)
			

if __name__ == '__main__':
	fname = sys.argv[1]  #fname is a list of people to update counts for ( one person per line )
	r = update_nums(fname)	
