#Diegos-MacBook-Pro:virtualenvs dolano$ virtualenv diegobs4
#Diegos-MacBook-Pro:virtualenvs dolano$ source diegobs4/bin/activate

import sys
from bs4 import BeautifulSoup
import requests
import json
import os
import time
import traceback

import getarticles_fromlinksjson

def get_page(url):
	print("GET url: "+url)
	page = requests.get(url) #,verify=False,timeout=20)
	soup = BeautifulSoup(page.content)
	return soup

def get_numpages(startsoup,starturl):
	numpages = 1
	try:
		pag_ul = startsoup.find('ul',{'class':'pagination'})
		lis = pag_ul.find_all('li')
		pageli = lis[len(lis)-2]
		a = pageli.find('a')
		href = a.attrs['href']
		urlparams = href.split("?page=")
		numpages = urlparams[1].split("&")[0]
	except:
		traceback.print_exc(file=sys.stdout)
		print "No pagination found so possible that numpages is 1 or there is a popup.. for second case wait 20 seconds then try again"
		time.sleep(20)
		try:
			pag_ul = startsoup.find('ul',{'class':'pagination'})
			lis = pag_ul.find_all('li')
			pageli = lis[len(lis)-2]
			a = pageli.find('a')
			href = a.attrs['href']
			urlparams = href.split("?page=")
			numpages = urlparams[1].split("&")[0]
		except:
			traceback.print_exc(file=sys.stdout)
			print "Second time through still no dice so leave as 1 so try regetting soup!"
			try:
				startsoup = get_page(starturl)			
				time.sleep(10)
				pag_ul = startsoup.find('ul',{'class':'pagination'})
				lis = pag_ul.find_all('li')
				pageli = lis[len(lis)-2]
				a = pageli.find('a')
				href = a.attrs['href']
				urlparams = href.split("?page=")
				numpages = urlparams[1].split("&")[0]
			except:
				traceback.print_exc(file=sys.stdout)
				print "Last time through still no dice so leave as 1 so try regetting soup!"

	return numpages, startsoup

def get_links(currentsoup,curlist):
	links = curlist
	storieslist = currentsoup.find('div',{'class':'stories'})
	articles = storieslist.find_all('article')
	for art in articles:
		h1 = art.find('h1')
		a = h1.find('a')
		title = h1.get_text()
		timeob = art.find('time')
		if timeob != None:
			time = timeob.attrs['title']
		else:
			time = ""
		
		if ".pdf" in a.attrs['href']:
			print "SKIP PDF FILE!" + a.attrs['href']
		else:
			links.append({'url':"www.texastribune.org"+a.attrs['href'],'title':title, 'time':time})
	return links

def save_list(filename,ob):
	print "Save "+filename+".json"
	with open(filename+".json", 'w') as outfile:
        	json.dump(ob, outfile)


def start(searchfor,savepath):
	starturl = 'http://www.texastribune.org/search/?page=1&q="'+searchfor+'"'
	print("\nIn Texas Tribune searching for "+searchfor+" with save path: "+savepath)

	#get html page
	startsoup = get_page(starturl)

	#get number of pages total
	numpages, startsoup = get_numpages(startsoup,starturl)
	print("Found "+str(numpages)+" pages of results")

	#get articles for first page
	articles = get_links(startsoup,[])

	#save partial result
	#save_list(searchfor.replace("+","_")+"-page1",articles)

	i = 2;
	while int(i) <= int(numpages):
		#url template
		cururl = 'http://www.texastribune.org/search/?page='+str(i)+'&q="'+searchfor+'"'
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

