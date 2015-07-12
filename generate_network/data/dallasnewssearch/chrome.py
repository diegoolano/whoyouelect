from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup
import requests
import traceback
import sys
import time

try:
	driver = webdriver.Chrome()
	#driver = webdriver.PhantomJS()
	driver.get('http://www.dallasnews.com/site-search/?q=Abel+Herrero')
	element = WebDriverWait(driver, 10).until(
	    EC.presence_of_element_located((By.CSS_SELECTOR, "td.gsc-table-cell-snippet-close"))
	)

	time.sleep(10)
	articles = driver.find_elements_by_css_selector("td.gsc-table-cell-snippet-close")
except:
	traceback.print_exc(file=sys.stdout)
	try:
		time.sleep(10)
		element = WebDriverWait(driver, 15)
		articles = driver.find_elements_by_css_selector("td.gsc-table-cell-snippet-close")
	except:
		traceback.print_exc(file=sys.stdout)
		



links = []
for a in articles:
	aurl = a.find_element_by_css_selector("a.gs-title").get_attribute("href")
	title = a.find_element_by_css_selector("a.gs-title").text
	time = a.find_element_by_css_selector("div.gs-snippet").text.split(" ...")[0]
	if "/author/" in aurl or "/tag/" in aurl:
		print "SKIP AUTHOR/TAG LINK: "+aurl
	elif "/blog/" in aurl: # and len(time) > 20:
		print "SKIP BLOG: "+aurl
	elif ".pdf" in aurl:
		print "SKIP PDF: "+aurl
	else:
		art_to_add = {'url':aurl,'title':title, 'time':time}
		if art_to_add not in links:
			print("ADD URL: "+aurl+ ", Title:" +title+", and Time: "+str(time))
			links.append(art_to_add)
		else:
			print "The following is already in links so skip it"
			print art_to_add
			print links

driver.quit()
