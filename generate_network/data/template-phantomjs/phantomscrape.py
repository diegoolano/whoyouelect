from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import sys
import json
import os
import time
import traceback

import getarticles_fromlinksjson

def get_links(driver,url,links):
	attempts = 1
	try:
		if url != "":
			driver.get(url)
			element = WebDriverWait(driver, 5).until(
			    EC.presence_of_element_located((By.CSS_SELECTOR, "ol.searchResultsList li.story"))
			)
	except TimeoutException:
		print("\t timeout error so retry")
		attempts = -1
		driver = ""
	except WebDriverException:
		print("\t webdriver exception")
		attempts = -1
		driver = ""

	if attempts == 1:
		articles = driver.find_elements_by_css_selector("ol.searchResultsList li.story")
		for a in articles:
			if a.text == "":
				print "Empty so skip"
				continue

			url = a.find_element_by_css_selector("h3 a")
			print "url: "+ str(url.__class__)
			if url.__class__ == "list":  
				continue
			url = url.get_attribute("href")

			title = a.find_element_by_css_selector("h3 a")
			#print "title: "+ str(title.__class__)
			if title.__class__ == "list":
				continue
			title = title.text

			time = a.find_element_by_css_selector("div.storyMeta span.dateline")
			#print "time: "+ str(time.__class__)
			time = time.text

			#print "URL: "+url+" | Title: "+ title + " | Date: "+ time
			links.append({'url':url,'title':title, 'time':time})

	return links

def get_next_tab(driver,pagenum):
	try:
		tabs = driver.find_element_by_css_selector("div.searchPagination a.next")
		if tabs != []:
			try:
				print "CLICK TAB: "+tabs.text
				pagenum = str(int(pagenum)+1)
				tabs.click()
				element = WebDriverWait(driver, 5).until(
				    EC.presence_of_element_located((By.CSS_SELECTOR, "ol.searchResultsList li.story"))
				)
				articles = driver.find_elements_by_css_selector("ol.searchResultsList li.story")
				for a in articles:
					if a.text == "":
						continue
					url = a.find_element_by_css_selector("h3 a")
					if url.__class__ == "list":  
						continue
					url = url.get_attribute("href")

					title = a.find_element_by_css_selector("h3 a")
					if title.__class__ == "list":
						continue
					title = title.text

					time = a.find_element_by_css_selector("div.storyMeta span.dateline")
					time = time.text

					#print "URL: "+url+" | Title: "+ title + " | Date: "+ time
			except TimeoutException:
				print("\t timeout error")
			except WebDriverException:
				print("\t webdriver exception")
	except:
		traceback.print_exc(file=sys.stdout)
		print "No next found.. check again, otherwise you are done"
		try:
			tabs = driver.find_element_by_css_selector("div.searchPagination a.next")
			if tabs != []:
				try:
					print "CLICK TAB: "#+tabs.text
					pagenum = str(int(pagenum)+1)
					tabs.click()
					element = WebDriverWait(driver, 5).until(
					    EC.presence_of_element_located((By.CSS_SELECTOR, "ol.searchResultsList li.story"))
					)
					articles = driver.find_elements_by_css_selector("ol.searchResultsList li.story")
					for a in articles:
						if a.text == "":
							continue
						url = a.find_element_by_css_selector("h3 a")
						if url.__class__ == "list":  
							continue
						url = url.get_attribute("href")

						title = a.find_element_by_css_selector("h3 a")
						if title.__class__ == "list":
							continue
						title = title.text

						time = a.find_element_by_css_selector("div.storyMeta span.dateline")
						time = time.text

						#print "URL: "+url+" | Title: "+ title + " | Date: "+ time
				except TimeoutException:
					print("\t timeout error")
				except WebDriverException:
					print("\t webdriver exception")
		except:
			traceback.print_exc(file=sys.stdout)
			print "No next found twice so no next"
	
	return [pagenum,driver]

def save_list(filename,ob):
	print "Save "+filename+".json"
	with open(filename+".json", 'w') as outfile:
        	json.dump(ob, outfile)


def start(searchfor,savepath):
	print("\nIn NYTimes searching for "+searchfor+" with save path: "+savepath)
	if "Texas+" in searchfor:
		searchfor = searchfor.replace("Texas+","").replace('"','')
		url = "http://query.nytimes.com/search/sitesearch/?action=click&contentCollection&region=TopBar&WT.nav=searchWidget&module=SearchSubmit&pgtype=Homepage#/Texas%22"+searchfor+"%22/since1851/allresults/1/allauthors/newest/"
	else:
		url = "http://query.nytimes.com/search/sitesearch/?action=click&contentCollection&region=TopBar&WT.nav=searchWidget&module=SearchSubmit&pgtype=Homepage#/%22"+searchfor+"%22/since1851/allresults/1/allauthors/newest/"
	
	print("GET url: "+url)
	driver = webdriver.PhantomJS()
	links = []
	links = get_links(driver,url,links)

	pagenum = 1
	endfound = False

	while endfound == False:
		nextpage,driver = get_next_tab(driver,pagenum)
		if nextpage == pagenum:
			endfound = True
		else:
			pagenum = nextpage
			print "Get Links for page: "+pagenum
			links = get_links(driver,"",links)
			

	#for saving purposes use _ instead of +
	searchfor = searchfor.replace("+","_")

	#check if folder searchfor exists
	if not os.path.exists(savepath+"/"+searchfor):
		os.makedirs(savepath+"/"+searchfor)
		#Save links json file in folder searchfor
		saveto = searchfor +"/" + "links-"+searchfor
	else:
		print "PATH: "+searchfor+" already exists so save file with date info"
		saveto = searchfor +"/" + "links-"+searchfor+ "-" + time.strftime("%d-%m-%y")


	#save_list(saveto,articles)
	save_list(savepath+"/"+saveto,links)
	print "Done.  Links file saved to "+savepath+"/"+saveto
	print "NOW get article information from links!"

	return getarticles_fromlinksjson.main_meth(searchfor.replace("_","+"),savepath)	


if __name__ == '__main__':
	searchfor = sys.argv[1].replace(" ","+")
	savepath = sys.argv[2]
	r = start(searchfor,savepath)	
