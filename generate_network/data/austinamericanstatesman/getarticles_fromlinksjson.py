import sys
from bs4 import BeautifulSoup
import requests
import json
import time
import wget

def get_page(url):
	print("GET url: "+url)
	try:
		time.sleep(2) 
		headers={"User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36"}
		with requests.Session() as s:
			#http://docs.python-requests.org/en/latest/api/
			page = s.get(url, headers=headers) #,verify=False,timeout=20)
			soup = BeautifulSoup(page.content)
			return soup
	except:
		e = sys.exc_info() ##[0]
		print e
		#try wget instead if needed!
		#page = wget.download(url)
		return ""

def get_article_text(artsoup):
	content = artsoup.find('span',{'class':'cm-story-dateline'});      #this maybe need to be div  cm-story-body
	if content != None and content != '':
		ps = content.find_all('p')
		return "\n".join([ p.get_text() for p in content.find_all('p')])
	else:
		return ""

def save_list(filename,ob):
	print "Save "+filename+".json"
	with open(filename+".json", 'w') as outfile:
        	json.dump(ob, outfile)

def main_meth(searchfor,savepath):
	#load json
	linksfile = savepath + "/" + searchfor.replace("+","_") + "/links-" + searchfor.replace("+","_") +".json"
	jsdata = open(linksfile,"r")
	links = json.load(jsdata)

	print("Getting "+str(len(links))+" articles worth of data from "+linksfile)

	for i,l in enumerate(links):
		if i >= 0:
			u = l['url']
			soup = get_page(u)
			if soup != "":
				text = get_article_text(soup)
				l['text'] = text
				l['news-source'] = "Austin American Statesman"
				l['article-num'] = "aas"+str(i)
				save_list(savepath+"/"+searchfor.replace("+","_") +"/"+l['article-num'],l)
			else:
				print("\tERROR: couldn't find article for url: "+u)

	return 1

if __name__ == '__main__':
	searchfor = sys.argv[1].replace(" ","+")
	savepath = sys.argv[2]
	r = main_meth(searchfor,savepath)
