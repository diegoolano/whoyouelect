import data.austinamericanstatesman.getlinksforlegislator as aas
import data.dallasnewssearch.phantomscrape as dmn
import data.houstonchronsearch.getlinksforlegislator as hc
import data.txobserver.phantomscrape as txob
import data.txtribune.getlinksforlegislator as txtrb
import data.nytimes.phantomscrape as nyt
import sys
import os
from data.delete_entity import delete_entity
from data.show_article_numbers_for import show_article_nums
import traceback

from multiprocessing import Pool
from shutil import copyfile, move

from pymongo import MongoClient
import time
#import add_json_files_for as aj      #this line caused it not to work!
#from add_json_files_for import *     #this also doesn't work so you have to do it via exec (or whatever to call python script via commandline )

#FUTURE TODO: do dynamic import of modules in data ( all folders except jsons and pickle ) so you don't need to add things by hand here
#see http://stackoverflow.com/questions/301134/dynamic-module-import-in-python

def callback_func(searcharg):
	#http://stackoverflow.com/questions/8533318/python-multiprocessing-pool-when-to-use-apply-apply-async-or-map
	print ("In Callback_func!!")
	#here we are done so call add_json_files_for.py with arg
	print "NOW CALLING add_json_files_for with "+searcharg
	#aj.start(searcharg)
	#start(searcharg)
	command = "python add_json_files_for.py '" + searcharg +"' > debug_and_backup_files/"+searcharg.replace(" ","_")+"-addjson-"+time.strftime("%m-%d_%I-%M-%S") + ".debug"
	print "UNIX CALL: "+command
	os.system(command)
		
def check_if_in_entity_db(searcharg):
	print "CHECK IF "+searcharg+" in Entity DB"
	conn = MongoClient()
	db = conn.newsdb   #db is called "newsdb"
	res = db.texnews.entities.find({"full_name":searcharg,"level": { "$in" : ["statewide-active","federal-active","statewide-active-elected"]}})
	if res.count() == 1:
		print "yes in entitydb"
		return [True,res]
	else:
		print "not in entitydb"
		return [False,'']
	
def show_summary(query,searchfor,searcharg):
	print("---DONE WITH DO_WEBSEARCH.PY---")	
	if query != searchfor:
		print "need move folders to correct places"
		#move(small_json_file,small_json_html)
		try:
			#ss = ["austinamericanstatesman","dallasnewssearch","houstonchronsearch","nytimes","txobserver","txtribune"]
			ss = []  #this is no longer necessary since its handled in nytimes/phantomscrape directly!
			folquery = query.replace('"','\"').replace("+","_")
			linksquery = query.replace("+","_")
			searchfor = searchfor.replace("+","_")
			for s in ss:
				oldentityfolder = "data/"+s+"/"+folquery
				newentityfolder = "data/"+s+"/"+searchfor
				oldlinksfile = "data/"+s+"/"+searchfor+"/links-"+linksquery+".json"
				newlinksfile = "data/"+s+"/"+searchfor+"/links-"+searchfor+".json"
				print "MOVE oldfolder: "+oldentityfolder+" TO newfolder: "+newentityfolder
				print "MOVE oldlinksfile: "+oldlinksfile+" TO newlinksfile: "+newlinksfile

				#move( oldentityfolder, newentityfolder )   #move from query with \"Rep_\"  to Allen_fisher
				#move( oldlinksfile, newlinksfile)  #move json file as well
				if os.path.exists(oldentityfolder):
					os.rename( oldentityfolder, newentityfolder )   #move from query with \"Rep_\"  to Allen_fisher
				else:
					print("ERROR couldn't find "+oldentityfolder)
				
				if os.path.exists(oldlinksfile):
					os.rename( oldlinksfile, newlinksfile)  #move json file as well
				else:
					print("ERROR couldn't find "+oldlinksfile)

		except:
			traceback.print_exc(file=sys.stdout)

	print("---Summary of Articles Obtained for "+searcharg+": ---")
	show_article_nums(searcharg)
	#os.system("python data/show_article_numbers_for.py '" + searcharg +"'")


def handle_results(pool,query,searchfor,searcharg,do_full):
	if 'answer1' in locals() and 'answer2' in locals() and 'answer3' in locals() and 'answer4' in locals() and 'answer5' in locals() and 'answer6' in locals():
		pool.close()
		pool.join()
		if do_full == "do_full":
			show_summary(query,searchfor,searcharg)
			print "argument do_full passed in so continue to populate db with json files, and generate small and medium sized networks"
			callback_func(searcharg)
		else:
			show_summary(query,searchfor,searcharg)
	else:
		print "NOT ALL RESULTS HAVE RETURNED YET so wait a little and then proceed!"
		time.sleep(60) #wait a minute and then go
		if 'answer1' in locals() and 'answer2' in locals() and 'answer3' in locals() and 'answer4' in locals() and 'answer5' in locals() and 'answer6' in locals():
			print "AGAIN NOT ALL RESULTS HAVE RETURNED YET so wait a little and then proceed!"
			time.sleep(60) #wait a minute and then go
			if 'answer1' in locals() and 'answer2' in locals() and 'answer3' in locals() and 'answer4' in locals() and 'answer5' in locals() and 'answer6' in locals():
				print "FINAL TIME NOT ALL RESULTS HAVE RETURNED YET so exit!"
				print "LOCAL VARS"
				print locals()
				sys.exit()
			else:
				pool.close()
				pool.join()
				print "ZZZZ FOUND ALL answers in locals2"
				if do_full == "do_full":
					show_summary(query,searchfor,searcharg)
					print "argument do_full passed in so continue to populate db with json files, and generate small and medium sized networks"
					callback_func(searcharg)
				else:
					show_summary(query,searchfor,searcharg)
		else:	
			pool.close()
			pool.join()
			print "ZZZZ FOUND ALL answers in locals1"
			if do_full == "do_full":
				show_summary(query,searchfor,searcharg)
				print "argument do_full passed in so continue to populate db with json files, and generate small and medium sized networks"
				callback_func(searcharg)
			else:
				show_summary(query,searchfor,searcharg)

def handle_single_result(answer,pool,query,searchfor,searcharg,do_full):
	if answer in locals():
		pool.close()
		pool.join()
		if do_full == "do_full":
			show_summary(query,searchfor,searcharg)
			print "argument do_full passed in so continue to populate db with json files, and generate small and medium sized networks"
			callback_func(searcharg)
		else:
			show_summary(query,searchfor,searcharg)
	else:
		print "RESULTS HAS NOT RETURNED YET so wait a little and then proceed!"
		time.sleep(60) #wait a minute and then go
		if answer in locals():
			print "AGAIN HAS  RETURNED YET so wait a little and then proceed!"
			time.sleep(60) #wait a minute and then go
			if answer in locals():
				print "FINAL TIME NOT ALL RESULTS HAVE RETURNED YET so exit!"
				print "LOCAL VARS"
				print locals()
				sys.exit()
			else:
				pool.close()
				pool.join()
				print "ZZZZ FOUND ALL answers in locals2"
				if do_full == "do_full":
					show_summary(query,searchfor,searcharg)
					print "argument do_full passed in so continue to populate db with json files, and generate small and medium sized networks"
					callback_func(searcharg)
				else:
					show_summary(query,searchfor,searcharg)
		else:	
			pool.close()
			pool.join()
			print "ZZZZ FOUND ALL answers in locals1"
			if do_full == "do_full":
				show_summary(query,searchfor,searcharg)
				print "argument do_full passed in so continue to populate db with json files, and generate small and medium sized networks"
				callback_func(searcharg)
			else:
				show_summary(query,searchfor,searcharg)

def begin_search(searchfor,savepath,do_full,only_source):
	searcharg = searchfor.replace("+"," ")
	#pool = Pool(processes=6)
	pool = Pool()

	success,res = check_if_in_entity_db(searcharg)
	if success == True:
		for n in res:
			#generate query out of name for nonTexas papers
			query = 'Texas "'+n['full_name']+'"'
			query = query.replace(" ","+")
	else:
		query = searchfor
	

	timeoutamount = 100000   #basically make timeout inifinite just to see if things work
	try:
		print "CALLING WEBSITES FOR SEARCHTERM: "+searchfor+" with path: "+savepath+" and QUERY: "+query
	except:
		try:
			print "CALLING WEBSITES FOR SEARCHTERM: "+searchfor
		except:
			print "In do_websearch.py with a searchfor I can't print to screen!"
		
	
	if only_source == False:
		result1 = pool.apply_async(aas.start, [searchfor,savepath+"/data/austinamericanstatesman/"])    
		result2 = pool.apply_async(dmn.start, [searchfor,savepath+"/data/dallasnewssearch/"])    
		result3 = pool.apply_async(hc.start, [searchfor,savepath+"/data/houstonchronsearch/"])    
		result4 = pool.apply_async(txob.start, [searchfor,savepath+"/data/txobserver/"])    
		result5 = pool.apply_async(txtrb.start, [searchfor,savepath+"/data/txtribune/"])    
		result6 = pool.apply_async(nyt.start, [query,savepath+"/data/nytimes/"])       #only nytimes should have weird folder

		try:
			result1.wait()
			result2.wait()
			result3.wait()
			result4.wait()
			result5.wait()
			result6.wait()

			answer1 = result1.get(timeout=timeoutamount)
			answer2 = result2.get(timeout=timeoutamount)
			answer3 = result3.get(timeout=timeoutamount)
			answer4 = result4.get(timeout=timeoutamount)
			answer5 = result5.get(timeout=timeoutamount)
			answer6 = result6.get(timeout=timeoutamount)
		except:
			traceback.print_exc(file=sys.stdout)
			sys.exit()
		finally:
			print "IN FINALLY.. HAVE ALL RESULTS COME BACK"	
			handle_results(pool,query,searchfor,searcharg,do_full)
	else:
		if only_source == 'austinamericanstatesman':
			result1 = pool.apply_async(aas.start, [searchfor,savepath+"/data/austinamericanstatesman/"])    
			try:
				result1.wait()
				answer1 = result1.get(timeout=timeoutamount)
				handle_single_result('answer1',pool,query,searchfor,searcharg,do_full)
			except:
				traceback.print_exc(file=sys.stdout)
				print "ERROR WITH WEBSEARCH SO STOPPING HERE"
				sys.exit()
		if only_source == 'dallasnewssearch':
			result2 = pool.apply_async(dmn.start, [searchfor,savepath+"/data/dallasnewssearch/"])    
			try:
				result2.wait()
				answer2 = result2.get(timeout=timeoutamount)
				handle_single_result('answer2',pool,query,searchfor,searcharg,do_full)
			except:
				traceback.print_exc(file=sys.stdout)
				print "ERROR WITH WEBSEARCH SO STOPPING HERE"
				sys.exit()
		if only_source == 'houstonchronsearch':
			result3 = pool.apply_async(hc.start, [searchfor,savepath+"/data/houstonchronsearch/"])    
			try:
				result3.wait()
				answer3 = result3.get(timeout=timeoutamount)
				handle_single_result('answer3',pool,query,searchfor,searcharg,do_full)
			except:
				traceback.print_exc(file=sys.stdout)
				print "ERROR WITH WEBSEARCH SO STOPPING HERE"
				sys.exit()
		if only_source == 'txobserver':
			result4 = pool.apply_async(txob.start, [searchfor,savepath+"/data/txobserver/"])    
			try:
				answer4 = result4.get(timeout=timeoutamount)
				handle_single_result('answer4',pool,query,searchfor,searcharg,do_full)
			except:
				traceback.print_exc(file=sys.stdout)
				print "ERROR WITH WEBSEARCH SO WAIT"
				time.sleep(60) 
				if os.path.isdir(savepath+"/data/txobserver/"+searcharg.replace(" ","_")):
					print "FOUND DIRECTORY: "+"/data/txobserver/"+searcharg.replace(" ","_")+" so handle new results!"
					handle_single_result('answer4',pool,query,searchfor,searcharg,do_full)
				else:
					print "AFTER WAIT DIDN'T FIND THINGS SO HARD EXIT!!"
					sys.exit()
		if only_source == 'txtribune':
			result5 = pool.apply_async(txtrb.start, [searchfor,savepath+"/data/txtribune/"])    
			try:
				result5.wait()
				answer5 = result5.get(timeout=timeoutamount)
				handle_single_result('answer5',pool,query,searchfor,searcharg,do_full)
			except:
				traceback.print_exc(file=sys.stdout)
				print "ERROR WITH WEBSEARCH SO STOPPING HERE"
				sys.exit()
		if only_source == 'nytimes':
			result6 = pool.apply_async(nyt.start, [query,savepath+"/data/nytimes/"])       #only nytimes should have weird folder
			try:
				result6.wait()
				answer6 = result6.get(timeout=timeoutamount)
				handle_single_result('answer6',pool,query,searchfor,searcharg,do_full)
			except:
				traceback.print_exc(file=sys.stdout)
				print "ERROR WITH WEBSEARCH SO STOPPING HERE"
				sys.exit()

			

if __name__ == '__main__':
	searchfor = sys.argv[1].replace(" ","+").replace("'","\'")
	#savepath = sys.argv[2]
	#savepath = os.path.dirname(os.path.realpath(__file__))
	savepath = "/Users/dolano/htdocs/dama-larca/d3/generate_network"

	if len(sys.argv) > 2:
		#if a second arg is included call add_json directly ( this will in turn make the small and medium json files and spit out debug info)
		do_full = sys.argv[2]   #do_full
	else:
		do_full = None
	
	if len(sys.argv) > 3:
		only_source = sys.argv[3]
	else:
		only_source = False

	if do_full == "showcountsonly":
		show_summary(sys.argv[1],sys.argv[1],sys.argv[1],False)
	else:
		#before hande remove folders if they exist
		print "---Delete old entity "+sys.argv[1]+" news articles if they exist---"
		if only_source == False:
			delete_entity(sys.argv[1],False)
		else:
			delete_entity(sys.argv[1],only_source)

		r = begin_search(searchfor,savepath,do_full,only_source)	
