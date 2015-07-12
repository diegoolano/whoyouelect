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
	
	print("DALLAS getlinks: "+url)
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
		except:
			traceback.print_exc(file=sys.stdout)
			print("\t timeout error so retry")
			try:
				time.sleep(10)
				element = WebDriverWait(driver, 10)
				articles = driver.find_elements_by_css_selector("td.gsc-table-cell-snippet-close")
				attempts = 1
			except:
				traceback.print_exc(file=sys.stdout)
				attempts = -1

	if attempts == 1:
		articles = driver.find_elements_by_css_selector("td.gsc-table-cell-snippet-close")
		for a in articles:
			url = a.find_element_by_css_selector("a.gs-title").get_attribute("href")
			title = a.find_element_by_css_selector("a.gs-title")
			timed = a.find_element_by_css_selector("div.gs-snippet")
			links.append({'url':url,'title':title.text, 'time':timed.text.split(" ...")[0]})

	return links

def get_next_tab(driver,pagenum):
	tabs = driver.find_elements_by_css_selector("div.gsc-cursor div")
	found = 0
	for t in tabs:
		if found == 2:
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
						url = a.find_element_by_css_selector("a.gs-title").get_attribute("href")
						title = a.find_element_by_css_selector("a.gs-title")
						timed = a.find_element_by_css_selector("div.gs-snippet")
						print "URL: "+url
						#print "Title: "+ title.text
						#print "Date: "+ timed.text.split(" ...")[0]
						#links.append({'url':url,'title':title.text, 'time':time.text.split(" ...")[0]})
					found = 2
				except TimeoutException:
					print("\t timeout error")
					found = 2
				except WebDriverException:
					print("\t webdriver exception")
					found = 2
	
	return [pagenum,driver]

def save_list(filename,ob):
	print "Save "+filename+".json"
	with open(filename+".json", 'w') as outfile:
        	json.dump(ob, outfile)


def check_for_long_open_time(url):
	print("Check "+url+" for popup!")
	worked = 0
	try:
		driver = webdriver.Chrome()
		driver.get(url)
		element = WebDriverWait(driver, 10).until(
		    EC.presence_of_element_located((By.CSS_SELECTOR, "td.gsc-table-cell-snippet-close"))
		)

		time.sleep(10)
		articles = driver.find_elements_by_css_selector("td.gsc-table-cell-snippet-close")
		worked = 1
	except:
		traceback.print_exc(file=sys.stdout)
		try:
			time.sleep(10)
			element = WebDriverWait(driver, 15)
			articles = driver.find_elements_by_css_selector("td.gsc-table-cell-snippet-close")
			worked = 1
		except:
			traceback.print_exc(file=sys.stdout)
			worked = 0
	if worked == 0:
		driver.quit()
		return [0,'']
	else:
		return [1,driver]

def start(searchfor,savepath):
	print("In Dallas Morning news searching for "+searchfor+" with save path: "+savepath)
	url = 'http://www.dallasnews.com/site-search/?q="'+searchfor+'"'
	print("call url: "+url)

	#check for initial block up or wait element to close!
	success,driver = check_for_long_open_time(url)

	print("POP to block: " +str(success))
	if success == 0:
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
			

	if success == 1:
		driver.quit() #close chrome if opened

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
