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

def get_numpages(startsoup):
	try:
		pag_ul = startsoup.find('div',{'class':'gsa-pagination'})     #THIS IS UNIQUE
		lis = pag_ul.find_all('li')				      #THIS IS UNIQUE  ..hmmm
		pageli = lis[len(lis)-2]
		a = pageli.find('a')
		href = a.attrs['href']
		urlparams = href.split("?page=")
		numpages = urlparams[1].split("&")[0]
	except:
		print("Either only one page of results or maybe lay out has changed")
		traceback.print_exc(file=sys.stdout)
		
		numpages = 1
		try:
			pag_ul = startsoup.find('div',{'class':'gsa-pagination'})     #THIS IS UNIQUE
			a = pag_ul.find_all('a')
			secondtolast = a[len(a)-2]
			numpages = secondtolast.get_text()
		except:
			print("At this point assume only one page of results")
			numpages = 1
			traceback.print_exc(file=sys.stdout)
		
	return numpages

def get_links(currentsoup,curlist):
	links = curlist
	try:
		storieslist = currentsoup.find('div',{'class':'gsa-search-results'})   #THIS IS UNIQUE
		articles = storieslist.find_all('div',{'class':'gsa-item'})            #THIS IS UNIQUE
		for art in articles:
			h2 = art.find('h2')                                            #THIS IS UNIQUE
			a = h2.find('a')							
			title = h2.get_text()
			timeob = art.find('span',{'class':'timestamp'})	
			if timeob != None:
				time = timeob.get_text()
			else:
				time = ""
			cura = a.attrs['href']
			if cura.find("http://") == -1:
				links.append({'url':"http://www.chron.com/"+a.attrs['href'],'title':title, 'time':time})
			else:
				links.append({'url': cura,'title':title, 'time':time})
		return links
	except:
		return links

def save_list(filename,ob):
	print "Save "+filename+".json"
	with open(filename+".json", 'w') as outfile:
        	json.dump(ob, outfile)


def start(searchfor,savepath):
	starturl = 'http://www.chron.com/search/?action=search&firstRequest=1&query="'+searchfor+'"&x=0&y=0&searchindex=gsa&sort=date'
	print("\nIn Houston Chronicle searching for "+searchfor+" with save path: "+savepath)

	#get html page
	startsoup = get_page(starturl)

	numpages = get_numpages(startsoup)
	print("HC Found "+str(numpages))

	#get articles for first page
	articles = get_links(startsoup,[])


	i = 2;
	if numpages > 1:
		endreached = False
		while endreached == False:
			#url template
			cururl = 'http://www.chron.com/search/?action=search&searchindex=gsa&query="'+searchfor+'"&sort=date&page='+str(i)
			cursoup = get_page(cururl)
			priorarticles = len(articles)
			articles = get_links(cursoup,articles)
			if len(articles) == priorarticles:
				endreached = True
			else:
				print "Currently in iteration "+str(i)+" with "+str(len(articles))+" calling get_newpages"
				nownum = get_numpages(cursoup)
				#if nownum == numpages:
				#	endreached = True
				#elif nownum > numpages:
				#	numpages = nownum
				#	i = i + 1
				#else:
				#	i = i + 1
				if nownum > numpages:
					numpages = nownum
					i = i + 1
				else:
					if i == numpages:
						print "At Last Page: i="+str(i)+" and numpages="+str(numpages)+" and nownum="+str(nownum)
						endreached = True
					else:
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
	print "Done.  Links file saved to "+saveto
	print "NOW get article information from links!"

	return getarticles_fromlinksjson.main_meth(searchfor,savepath)	


if __name__ == '__main__':
	searchfor = sys.argv[1].replace(" ","+")
	savepath = sys.argv[2]
	r = start(searchfor,savepath)	

