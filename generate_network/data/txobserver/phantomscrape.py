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
	
	url = url.replace('"','')
	print("TXOBSERVER getlinks: "+url)
	attempts = 1
	try:
		if url != "":
			driver.get(url)
			time.sleep(10)
			element = WebDriverWait(driver, 10).until(
			    EC.presence_of_element_located((By.CSS_SELECTOR, "td.gsc-table-cell-snippet-close"))
			)
			print("no prob")
	except TimeoutException:
		print("\t timeout error so retry")
		try:
			element = WebDriverWait(driver, 10).until(
			    EC.presence_of_element_located((By.CSS_SELECTOR, "td.gsc-table-cell-snippet-close"))
			)

			time.sleep(10)
			articles = driver.find_elements_by_css_selector("td.gsc-table-cell-snippet-close")
			attempts = 1
			print("no prob1")
		except:
			traceback.print_exc(file=sys.stdout)
			print("\t timeout error so retry2")
			try:
				time.sleep(10)
				element = WebDriverWait(driver, 10)
				articles = driver.find_elements_by_css_selector("td.gsc-table-cell-snippet-close")
				attempts = 1
				print("no prob2")
			except:
				traceback.print_exc(file=sys.stdout)
				print("\t exit error")
				attempts = -1

	if attempts == 1:
		print "IN ATTEMPTS 1"
		articles = driver.find_elements_by_css_selector("td.gsc-table-cell-snippet-close")
		for a in articles:
			#url = a.find_element_by_css_selector("a.gs-title").get_attribute("href")
			#title = a.find_element_by_css_selector("a.gs-title")
			#timed = a.find_element_by_css_selector("div.gs-snippet")
			#links.append({'url':url,'title':title.text, 'time':timed.text.split(" ...")[0]})

			aurl = a.find_element_by_css_selector("a.gs-title").get_attribute("href")
			title = a.find_element_by_css_selector("a.gs-title").text
			ptime = a.find_element_by_css_selector("div.gs-snippet").text
			if "/author/" in aurl or "/tag/" in aurl:
				print "SKIP AUTHOR/TAG LINK: "+aurl
			elif "/blog/" in aurl: # and len(time) > 20:
				print "SKIP BLOG: "+aurl
			elif ".pdf" in aurl:
				print "SKIP PDF: "+aurl
			else:
				art_to_add = {'url':aurl,'title':title, 'time':ptime.split(" ...")[0]}
				if art_to_add not in links:
					#print("ADD URL: "+aurl+ ", Title:" +title+", and Time: "+str(time))
					print("ADD URL: "+aurl)
					links.append(art_to_add)
				else:
					print "The following is already in links so skip it"
					print art_to_add
					print links

	return links

def get_next_tab(driver,pagenum):
	tabs = driver.find_elements_by_css_selector("div.gsc-cursor div")
	found = 0
	for t in tabs:
		if found == 2:
			print "NOW GET ARTICLES FROM PAGE "+str(pagenum)
			break
		elif "gsc-cursor-current-page" in t.get_attribute("class"):
			found = 1
		else:
			if found == 1:
				try:
					print "CLICK TAB: "+t.text
					pagenum = t.text
					t.click()
					time.sleep(10)
					element = WebDriverWait(driver, 10).until(
					    EC.presence_of_element_located((By.CSS_SELECTOR, "td.gsc-table-cell-snippet-close"))
					)
					articles = driver.find_elements_by_css_selector("td.gsc-table-cell-snippet-close")
					for a in articles:
						print("\t --now on ")
						url = a.find_element_by_css_selector("a.gs-title").get_attribute("href")
						title = a.find_element_by_css_selector("a.gs-title")
						ptime = a.find_element_by_css_selector("div.gs-snippet")
						print "\t -- URL: "+url
						#print "Title: "+ title.text
						#print "Date: "+ time.text.split(" ...")[0]
						#links.append({'url':url,'title':title.text, 'time':time.text.split(" ...")[0]})
					found = 2
				except TimeoutException:
					print("\t timeout error3")
					found = 2
				except WebDriverException:
					print("\t webdriver exception3")
					found = 2

	return [pagenum,driver]

def save_list(filename,ob):
	print "Save "+filename+".json"
	with open(filename+".json", 'w') as outfile:
        	json.dump(ob, outfile)


def check_for_blocking_popup(url):
	print("Check "+url+" for popup!")
	worked = 0
	try:
		driver = webdriver.Chrome()
		driver.get(url)
		element = WebDriverWait(driver, 10).until(
		    EC.presence_of_element_located((By.CSS_SELECTOR, "div#cboxClose"))
		)

		time.sleep(10)
		l = element.find_element_by_css_selector("div#cboxClose")
		l.click()
		element = WebDriverWait(driver, 15)
		articles = driver.find_elements_by_css_selector("td.gsc-table-cell-snippet-close")
		worked = 1
	except:
		traceback.print_exc(file=sys.stdout)
		try:
			traceback.print_exc(file=sys.stdout)
			time.sleep(10)
			l = driver.find_element_by_css_selector("div#cboxClose")
			l.click()
			element = WebDriverWait(driver, 15)
			articles = driver.find_elements_by_css_selector("td.gsc-table-cell-snippet-close")
			worked = 1
		except:	
			worked = 0
			traceback.print_exc(file=sys.stdout)
	
	if worked == 0:
		driver.quit()
		return [0,'']
	else:
		return [1,driver]


def start(searchfor,savepath):
	print("\nIn Texas Observer searching for "+searchfor+" with save path: "+savepath)
	url = 'http://www.texasobserver.org/search-results/?q="'+searchfor+'"'
	print("call url: "+url)


	#check for initial block up or wait element to close!
	success,driver = check_for_blocking_popup(url)

	print("POP to block: " +str(success))
	if success == 0:
		driver = webdriver.PhantomJS()

	links = []
	links = get_links(driver,url,links)
	print "After first page we have "+str(len(links))+" links"
	print "\n".join([f['url'] for f in links])

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
			print "After pagenum "+str(pagenum)+" we have "+str(len(links))+" links"
			print "\n".join([f['url'] for f in links])
			

	print "OBSERVER Done with getting links"
	if success == 1:
		driver.quit()  #close chrome tab if opened

	#for saving purposes use _ instead of +
	searchfor = searchfor.replace("+","_")

	print "CHECK IF FOLDER "+searchfor+" EXISTS IN OBSERVER FOLDER"
	#check if folder searchfor exists
	if not os.path.exists(savepath+"/"+searchfor):
		print "No, so make folder"
		os.makedirs(savepath+"/"+searchfor)
		#Save links json file in folder searchfor
		saveto = searchfor +"/" + "links-"+searchfor
	else:
		print "PATH: "+searchfor+" already exists so save file with date info"
		saveto = searchfor +"/" + "links-"+searchfor+ "-" + time.strftime("%d-%m-%y")

	#save_list(saveto,articles)
	save_list(savepath+"/"+saveto,links)
	print "OBSERVER Done.  Links file saved to "+savepath+"/"+saveto
	print "NOW get article information from links!"

	return getarticles_fromlinksjson.main_meth(searchfor.replace("_","+"),savepath)	

if __name__ == '__main__':
	searchfor = sys.argv[1].replace(" ","+")
	savepath = sys.argv[2]
	r = start(searchfor,savepath)	
