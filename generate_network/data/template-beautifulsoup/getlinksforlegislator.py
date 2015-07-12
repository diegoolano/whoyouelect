#source ~/virtualenvs/diegobs4/bin/activate
import sys
from bs4 import BeautifulSoup
import requests
import json
import os
import time

import getarticles_fromlinksjson

def get_page(url):
	print("GET url: "+url)
	page = requests.get(url) #,verify=False,timeout=20)
	soup = BeautifulSoup(page.content)
	return soup

def get_numpages(startsoup):
	pag_ul = startsoup.find('div',{'class':'cm-list-item-count'})
	numpages =  int(pag_ul.get_text().replace("\n","").replace(" ","").replace("items",""))
	return numpages

def get_links(currentsoup,curlist):
	links = curlist
	storieslist = currentsoup.find('div',{'class':'cm-list-box'})
	if storieslist != None and storieslist != '':
		articles = storieslist.find_all('div',{'class':'cm-list-item'})
		for art in articles:
			h1 = art.find('h3')
			a = h1.find('a')
			title = h1.get_text()
			timeob = art.attrs['data-published']
			if timeob != None:
				time = art.attrs['data-published']
			else:
				time = ""
			links.append({'url':""+a.attrs['href'],'title':title, 'time':time})
	return links

def save_list(filename,ob):
	print "Save "+filename+".json"
	with open(filename+".json", 'w') as outfile:
        	json.dump(ob, outfile)


def start(searchfor,savepath):
	starturl = 'http://www.statesman.com/search/?q="'+searchfor+'"&page=1'
	print("In Austin American Statesman searching for "+searchfor+" with save path: "+savepath)

	#get html page
	startsoup = get_page(starturl)

	#get number of pages total
	numpages = get_numpages(startsoup)
	print("Found "+str(numpages)+" pages of results")

	#get articles for first page
	articles = get_links(startsoup,[])

	i = 2
	while int(i) <= int(numpages):
		#url template
		cururl = 'http://www.statesman.com/search/?page='+str(i)+'&q="'+searchfor+'"'
		cursoup = get_page(cururl)
		articles = get_links(cursoup,articles)
		i = i + 1


	#check if folder searchfor exists
	if not os.path.exists(savepath+"/"+searchfor):
		os.makedirs(savepath+"/"+searchfor.replace("+","_"))
		#Save links json file in folder searchfor
		saveto = searchfor.replace("+","_") +"/" + "links-"+searchfor.replace("+","_")
	else:
		print "PATH: "+searchfor+" already exists so save file with date info"
		saveto = searchfor.replace("+","_") +"/" + "links-"+searchfor.replace("+","_") + "-" + time.strftime("%d-%m-%y")

	save_list(savepath+"/"+saveto,articles)
	print "Done.  Links file saved to "+savepath+"/"+saveto
	print "NOW get article information from links!"

	return getarticles_fromlinksjson.main_meth(searchfor,savepath)	


if __name__ == '__main__':
	searchfor = sys.argv[1].replace(" ","+")
	savepath = sys.argv[2]
	r = start(searchfor,savepath)	
