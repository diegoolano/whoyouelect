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
		time.sleep(2) 
		headers={"User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36"}
		with requests.Session() as s:
			#http://docs.python-requests.org/en/latest/api/
			page = s.get(url, headers=headers ,verify=False,timeout=20)
			soup = BeautifulSoup(page.content)
			return soup
	except:
		e = sys.exc_info() ##[0]
		print e
		#try wget instead if needed!
		#page = wget.download(url)
		return ""


def get_article_text(artsoup,posttype,errorfile):
	if posttype == "normal":
		content = artsoup.find('div',{'class':'article-body'})                   #THIS IS UNIQUE
		if content!= None and content != '':
			ps = content.find_all('p')						 #THIS IS UNIQUE
			return "\n".join([ p.get_text() for p in content.find_all('p')])
		else:
			#try image gallery
			content = artsoup.find_all('div',{'class':'smImageCaption'})                   #THIS IS UNIQUE
			if content != None and content != '':
				print "WORKED WORKED image with errorfile: "+errorfile
			
				if errorfile != "":
					os.remove(errorfile)	
				
				ret = "\n".join([ p.get_text() for p in content])
				if ret =="":
					content2 = artsoup.find_all('div',{'class':'gallery-caption'})                   #THIS IS UNIQUE
					if content2 != None and content2 != '':
						print "WORKED WORKED WORKED image with errorfile: "+errorfile
						#print content2
						#return "\n".join([ p.get_text() for p in content2])
						#THIS DOESN'T WORK BECAUSE ITS JS BASED.. WE'LL NEED PHANTOMJS FOR IT
						return ""
				else:
					return ret
			else:
				print "EMPTY IMAGEGALLERY?"
				return ""
	elif posttype == "blog":
		content = artsoup.find('div',{'class':'entry'})                   #THIS IS UNIQUE
		if content != None and content != '':
			ps = content.find_all('p')						 #THIS IS UNIQUE
			print "WORKED WORKED"
		
			if errorfile != "":
				os.remove(errorfile)	
			
			return "\n".join([ p.get_text() for p in content.find_all('p')])
		else:
			print "EMPTY BLOGPOST?"
			return ""
	else:
		print "ERROR posttype not found"	

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
	hcfiles = [ f for f in listdir(mypath) if isfile(join(mypath,f)) and str(f).find("error") > -1 ]

	for i,l in enumerate(links):
		errorfile = searchfor+"-hc_"+str(i)+"error.html" 
		if errorfile in hcfiles or i > -1: 
			if i > -1:
				errorfile = ""

			print(str(i)+"---------")
			u = l['url']
			soup = get_page(u)
			posttype = "normal"
			if "http://blog.chron.com/" in u:
				posttype = "blog"
			text = get_article_text(soup,posttype,errorfile)
			l['text'] = text
			l['news-source'] = "HOUSTON CHRONICLE"      #THIS IS UNIQUE
			l['article-num'] = "hc_"+str(i)             #THIS IS UNIQUE
			if text != "":
				save_list(savepath + "/"+ searchfor + "/" + searchfor+"-"+l['article-num'],l)
			else:
				with open(savepath + "/" +searchfor + "/" + searchfor+"-"+l['article-num']+"error.html", 'w') as outfile:
					outfile.write(soup.prettify().encode("utf-8"))
	
	return 1


if __name__ == '__main__':
	searchfor = sys.argv[1].replace(" ","+")
	savepath = sys.argv[2]
	r = main_meth(searchfor,savepath)
