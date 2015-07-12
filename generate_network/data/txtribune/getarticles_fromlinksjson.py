import sys
from bs4 import BeautifulSoup
import requests
import json
import time
import os

from os import listdir
from os.path import isfile, join
from os import getcwd

def get_page(url):
	print("GET url: "+url)
	time.sleep(2) 
	try:
		page = requests.get("http://"+url) #,verify=False,timeout=20)
		soup = BeautifulSoup(page.content)
		return soup
	except:
		return ""

def get_article_text(artsoup):
	content = artsoup.find('div',{'class':'content'})
	if content!= None and content != '':
		ps = content.find_all('p')
		return "\n".join([ p.get_text() for p in content.find_all('p')])
	else:
		print "ERROR"
		return ''

def save_list(filename,ob):
	print "Save "+filename+".json"
	with open(filename+".json", 'w') as outfile:
        	json.dump(ob, outfile)

def main_meth(searchfor,savepath):
	#load json
	searchfor = searchfor.replace("+","_")
	linksfile = savepath + "/" +searchfor + "/links-" + searchfor +".json"
	jsdata = open(linksfile,"r")
	links = json.load(jsdata)
	mypath = savepath + "/" + searchfor.replace("+","_")
	print("Getting "+str(len(links))+" articles worth of data from "+linksfile)


	for i,l in enumerate(links):
		u = l['url']
		soup = get_page(u)
		text = get_article_text(soup)
		l['text'] = text
		l['news-source'] = "Texas Tribune"
		l['article-num'] = "txtb"+str(i)
		#save_list(l['article-num'],l)
		if text != "":
			save_list(savepath + "/" + searchfor + "/" + searchfor+"-"+l['article-num'],l)
		else:
			with open(savepath + "/" +searchfor + "/" + searchfor+"-"+l['article-num']+"error.html", 'w') as outfile:
				outfile.write(soup.prettify().encode("utf-8"))
	

	return 1

if __name__ == '__main__':
	searchfor = sys.argv[1].replace(" ","+")
	savepath = sys.argv[2]
	r = main_meth(searchfor,savepath)
