# coding: latin-1
from dama_globals import *
from dama_utils import *
from dama_ner import *
from entity_funcs import *
from handle_funcs import *
from verify_and_save_relations import *
import time
import traceback

'''
from __future__ import unicode_literals
from ftfy import fix_text
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters
import json
import sys
from functools import wraps
import errno
import os
import signal
from pymongo import MongoClient

'''
import nltk
import string
import os
import sys

#https://github.com/mneedham/neo4j-qcon/blob/master/topics.py
import csv

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF
from collections import defaultdict
#from bs4 import BeautifulSoup, NavigableString
#from soupselect import select

def uri_to_file_name(uri):
    return uri.replace("/", "-")
###

import datetime
from dateutil.parser import *
import traceback
def handle_date(art):
	success = 0
	try:
		if 'date' not in art:
			if 'time' in art:
				date_text = art['time']
				dt = parse(date_text)	
				ntime = dt.strftime("%Y-%m-%d")
				art['date'] = ntime
				del art['time']
				success = 1
			else:
				print("ERROR couldn't find 'date' or 'time' in article:")
				print(art)
		else:
			date_text = art['date']
			dt = parse(date_text)	
			ntime = dt.strftime("%Y-%m-%d")
			art['date'] = ntime
			success = 1
			
	except:
		try:
			years = range(2000,2015) 
			for y in years:
				if str(y) in art["url"]:
					pos = art["url"].index(str(y))
					posend = pos + 1
					while posend < len(art["url"]):
						try:
							x = int(art["url"][posend])
							posend = posend + 1
						except:
							date_text = art["url"][pos:posend]
							dt = parse(date_text)
							ntime = dt.strftime("%Y-%m-%d")
							art['date'] = ntime
							if 'time' in art: del art['time']
							success = 1
							#print("NEWDATE: "+date_text)
							break
					break
			if success == 0:
				#print("In HANDLE DATE WITH ART: "+art["url"]+" .. BAD DATE FORMAT IN JSON SO LOOK IN URL FOR A DATE OR JUST GIVE IT A DUMMY DATE")    #Abel Herrero 59,68,75,124,125
				#still no luck so default to dummy date of 2000-01-01
				dt = parse("2000-01-01")
				ntime = dt.strftime("%Y-%m-%d")
				art['date'] = ntime 
				if 'time' in art: del art['time']
				#print("NEWDATE: DEFAULT: 2000-01-01")
				success = 1
		except:
			print("STILL COULDNT HANDLE DATE SO SKIP ARTICLE")
			traceback.print_exc(file=sys.stdout)
				
			

	return [success,art]

'''
conn = MongoClient()
db = conn.newsdb   #db is called "newsdb"

punkt_param = PunktParameters()
sentence_splitter = PunktSentenceTokenizer(punkt_param)
'''

#generated list by the following query in mongo:    db.texnews.entities.distinct("full_name").sort()
#entitieslist = [ "Aaron Peña", "Abel Herrero", "Al Edwards", "Al Green", "Allan Ritter", "Allen Fletcher", "Allen Vaught", "Alma Allen", "Ana Hernandez", "Andrew Murr", "Angie Chen Button", "Armando Martinez", "Armando Walle", "Barbara Legler", "Barbara Mallory Caraway", "Barbara Nash", "Barbara Parker Hervey", "Bennett Ratliff", "Bert Richardson", "Beto Rourke", "Betty Brown", "Beverly Woolley", "Bill Flores", "Blake Farenthold", "Bob Deuell", "Bob Hall", "Bobby Guerra", "Borris L. Miles", "Brandon Creighton", "Brian Babin", "Brian Birdwell", "Brooks Landgraf", "Bryan Hughes", "Burt Solomons", "Byron Cook", "Carl Isett", "Carlos Uresti", "Carol Alvarado", "Carol Kent", "Cecil Bell", "Celia Israel", "Charles Anderson", "Charles Perry", "Charles Schwertner", "Charlie Geren", "Charlie Howard", "Chente Quintanilla", "Cheryl Johnson", "Chris Harris", "Chris Paddie", "Chris Turner", "Christi Craddick", "Chuck Hopson", "Cindy Burkett", "Connie Scott", "Craig Eiland", "Craig Estes", "Craig Goldman", "César José Blanco", "Dade Phelan", "Dan Branch", "Dan Flynn", "Dan Gattis", "Dan Huberty", "Dan Patrick", "David Dewhurst", "David Farabee", "David Leibowitz", "David Newell", "David Porter", "David Simpson", "David Swinford", "Dawnna Dukes", "DeWayne Burns", "Debbie Riddle", "Debra Lehrmann", "Dee Margo", "Delwin Jones", "Dennis Bonnen", "Dennis Paul", "Diana Maldonado", "Diane Patrick", "Diego Bernal", "Don Huffines", "Don R. Willett", "Donna Campbell", "Donna Howard", "Dora Olivo", "Doug Miller", "Drew Darby", "Drew Springer", "Dustin Burrows", "Dwayne Bohac", "Ed Thompson", "Eddie Johnson", "Eddie Lucio III", "Eddie Lucio Jr", "Eddie Rodriguez", "Edmund Kuempel", "Eliot Shapleigh", "Ellen Cohen", "Elliott Naishtat", "Elsa Alcala", "Eric Johnson", "Erwin Cain", "Eva M. Guzman", "Filemon Vela", "Florence Shapiro", "Four Price", "Frank Corte Jr.", "Fred Brown", "Garnet Coleman", "Gary Elkins", "Gary VanDeaver", "Geanie Morrison", "Gene Green", "Gene Wu", "George Lavender", "George P. Bush", "Gilbert Peña", "Giovanni Capriglione", "Glenn Hegar", "Greg Abbott", "Greg Bonnen", "Harold Dutton", "Harvey Hilderbran", "Helen Giddings", "Henry Cuellar", "Hubert Vo", "Ina Minjarez", "J. M. Lozano", "J.D. Sheffield", "James Frank", "James White", "Jane Nelson", "Jason Isaac", "Jason Villalba", "Jeb Hensarling", "Jeff Brown", "Jeff Leach", "Jeff Wentworth", "Jeffrey S. Boyd", "Jerry Madden", "Jessica Farrar", "Jim Dunnam", "Jim Jackson", "Jim Keffer", "Jim Landtroop", "Jim McReynolds", "Jim Murphy", "Jim Pitts", "Jimmie Don Aycock", "Joan Huffman", "Joaquin Castro", "Jodie Laubenberg", "Joe Barton", "Joe Crabb", "Joe Deshotel", "Joe Driver", "Joe Farias", "Joe Heflin", "Joe Pickett", "Joe Straus", "John Carona", "John Carter", "John Cornyn", "John Culberson", "John Cyrier", "John Davis", "John Devine", "John Frullo", "John Garza", "John Kuempel", "John Otto", "John Raney", "John Ratcliffe", "John Smithee", "John Whitmire", "John Wray", "John Zerwas", "Jonathan Stickland", "Jose Aliseda", "Jose Menendez", "Jose Rodriguez", "Joseph Moody", "Juan Hinojosa", "Judith Zaffirini", "Justin Rodriguez", "Kay Granger", "Kel Seliger", "Kelly Hancock", "Ken King", "Ken Legler", "Ken Paxton", "Kenneth Sheets", "Kenny Marchant", "Kevin Brady", "Kevin Eltife", "Kevin Yeary", "Kino Flores", "Kip Averitt", "Kirk England", "Kirk Watson", "Konni Burton", "Kristi Thibaut", "Kyle Kacal", "Lamar Smith", "Lance Gooden", "Lanham Lyne", "Larry Gonzales", "Larry Phillips", "Larry Taylor", "Lawrence E. Meyers", "Leighton Schubert", "Leo Berman", "Leticia Van de Putte", "Linda Harper-Brown", "Linda Koop", "Lloyd Doggett", "Lois Kolkhorst", "Lon Burnam", "Louie Gohmert", "Lyle Larson", "Mac Thornberry", "Marc Veasey", "Mario Gallegos Jr.", "Marisa Marquez", "Mark Homer", "Mark Keough", "Mark Shelton", "Mark Strama", "Marsha Farney", "Marva Beck", "Mary González", "Mary Perez", "Matt Krause", "Matt Rinaldi", "Matt Schaefer", "Matt Shaheen", "Michael Burgess", "Michael E. Keasler", "Michael McCaul", "Mike Conaway", "Mike Hamilton", "Mike Jackson", "Mike Schofield", "Mike Villarreal", "Molly White", "Morgan Meyer", "Myra Crownover", "Naomi Gonzalez", "Nathan L. Hecht", "Nicole Collier", "Norma Chavez", "Oscar Longoria", "Pat Fallon", "Patricia Harless", "Patrick Rose", "Paul Bettencourt", "Paul Green", "Paul Workman", "Paula Pierson", "Pete Gallego", "Pete Olson", "Pete Sessions", "Phil Johnson", "Phil King", "Phil Stephenson", "Philip Cortez", "Poncho Nevárez", "Rafael Anchia", "Ralph Sheffield", "Ramon Romero", "Randy Neugebauer", "Randy Weber", "Raul Torres", "Rene Oliveira", "Richard Peña Raymond", "Rick Galindo", "Rick Hardcastle", "Rick Miller", "Rob Eissler", "Rob Orr", "Robert Duncan", "Robert Miklos", "Robert Nichols", "Roberto Alonzo", "Rodney Anderson", "Rodney Ellis", "Roger Williams", "Roland Gutierrez", "Ron Reynolds", "Ron Simmons", "Royce West", "Ruben Hinojosa", "Ruth Jones McClendon", "Ryan Guillen", "Ryan Sitton", "Sam Johnson", "Sarah Davis", "Scott Hochberg", "Scott Sanford", "Scott Turner", "Senfronia Thompson", "Sergio Muñoz, Jr.", "Sharon Keller", "Sheila Jackson Lee", "Sid Miller", "Solomon Ortiz Jr.", "Stefani Carter", "Stephanie Klick", "Stephen Frost", "Steve Ogden", "Steve Toth", "Stuart Spitzer", "Susan King", "Sylvester Turner", "Sylvia Garcia", "Tan Parker", "Tara Rios Ybarra", "Ted Cruz", "Ted Poe", "Terry Canales", "Tim Kleinschmidt", "Todd Hunter", "Todd Smith", "Tom Craddick", "Tommy Merritt", "Tommy Williams", "Toni Rose", "Tony Dale", "Tony Tinderholt", "Tracy King", "Travis Clardy", "Trent Ashby", "Trey Martinez Fischer", "Troy Fraser", "Tryon Lewis", "Valinda Bolton", "Van Taylor", "Veronica Gonzales", "Vicki Truitt", "Warren Chisum", "Wayne Christian", "Wayne Faircloth", "Wayne Smith", "Wendy Davis", "Will Hartnett", "Will Hurd", "Will Metcalf", "William Callegari", "William Zedler", "Yvonne Davis", "Yvonne Gonzalez Toureilles" ]

#list above included inactive people and some accent marks that differ from front end.. instead use search_terms from config.json
#Object.keys(search_terms).sort().join('","')
entitieslist = ["Abel Herrero","Al Green","Allen Fletcher","Alma Allen","Ana Hernandez","Andrew Murr","Angie Chen Button","Armando Martinez","Armando Walle","Barbara Hervey","Bert Richardson","Beto Rourke","Bill Flores","Bill Zedler","Blake Farenthold","Bob Hall","Bob Libal","Bobby Guerra","Borris Miles","Brandon Creighton","Brian Babin","Brian Birdwell","Brooks Landgraf","Bryan Hughes","Byron Cook","Carlos Uresti","Carol Alvarado","Cecil Bell","Celia Israel","Cesar Blanco","Charles Anderson","Charles Perry","Charles Schwertner","Charlie Geren","Cheryl Johnson","Chris Paddie","Chris Turner","Christi Craddick","Cindy Burkett","Craig Estes","Craig Goldman","Dade Phelan","Dan Flynn","Dan Huberty","Dan Patrick","David Newell","David Porter","David Simpson","Dawnna Dukes","DeWayne Burns","Debbie Riddle","Debra Lehrmann","Dennis Bonnen","Dennis Paul","Diego Bernal","Don Huffines","Don Willett","Donna Campbell","Donna Howard","Doug Miller","Drew Darby","Drew Springer","Dustin Burrows","Dwayne Bohac","Ed Thompson","Eddie Johnson","Eddie Lucio III","Eddie Lucio Jr","Eddie Rodriguez","Elliott Naishtat","Elsa Alcala","Eric Johnson","Eva Guzman","Filemon Vela","Four Price","Garnet Coleman","Gary Elkins","Gary VanDeaver","Geanie Morrison","Gene Green","Gene Wu","George P. Bush","Gilbert Pena","Giovanni Capriglione","Glenn Hegar","Greg Abbott","Greg Bonnen","Harold Dutton","Helen Giddings","Henry Cuellar","Hubert Vo","Ina Minjarez","J. M. Lozano","J.D. Sheffield","James Frank","James White","Jane Nelson","Jason Isaac","Jason Villalba","Jeb Hensarling","Jeff Brown","Jeff Leach","Jeffrey Boyd","Jessica Farrar","Jim Keffer","Jim Murphy","Jimmie Don Aycock","Joan Huffman","Joaquin Castro","Jodie Laubenberg","Joe Barton","Joe Deshotel","Joe Farias","Joe Pickett","Joe Straus","John Carter","John Cornyn","John Culberson","John Cyrier","John Devine","John Frullo","John Kuempel","John Otto","John Raney","John Ratcliffe","John Smithee","John Whitmire","John Wray","John Zerwas","Jonathan Stickland","Jose Menendez","Jose Rodriguez","Joseph Moody","Juan Hinojosa","Judith Zaffirini","Justin Rodriguez","Kay Granger","Kel Seliger","Kelly Hancock","Ken King","Ken Paxton","Kenneth Sheets","Kenny Marchant","Kevin Brady","Kevin Eltife","Kevin Yeary","Kirk Watson","Konni Burton","Kyle Kacal","Lamar Smith","Larry Gonzales","Larry Phillips","Larry Taylor","Lawrence Meyers","Leighton Schubert","Linda Koop","Lloyd Doggett","Lois Kolkhorst","Louie Gohmert","Lyle Larson","Mac Thornberry","Marc Veasey","Marisa Marquez","Mark Keough","Marsha Farney","Mary Gonzalez","Matt Krause","Matt Rinaldi","Matt Schaefer","Matt Shaheen","Michael Burgess","Michael Keasler","Michael McCaul","Mike Conaway","Mike Schofield","Molly White","Morgan Meyer","Myra Crownover","Nathan Hecht","Nicole Collier","Oscar Longoria","Pat Fallon","Patricia Harless","Paul Bettencourt","Paul Green","Paul Workman","Pete Olson","Pete Sessions","Phil Johnson","Phil King","Phil Stephenson","Poncho Nevarez","Rafael Anchia","Ramon Romero","Randy Neugebauer","Randy Weber","Rene Oliveira","Richard Raymond","Rick Galindo","Rick Miller","Robert Nichols","Roberto Alonzo","Rodney Anderson","Rodney Ellis","Roger Williams","Roland Gutierrez","Ron Reynolds","Ron Simmons","Royce West","Ruben Hinojosa","Ruth Jones McClendon","Ryan Guillen","Ryan Sitton","Sam Johnson","Sarah Davis","Scott Sanford","Scott Turner","Senfronia Thompson","Sergio Munoz","Sharon Keller","Sheila Jackson Lee","Sid Miller","Stephanie Klick","Stuart Spitzer","Susan King","Sylvester Turner","Sylvia Garcia","Tan Parker","Ted Cruz","Ted Poe","Terry Canales","Todd Hunter","Tom Craddick","Toni Rose","Tony Dale","Tony Tinderholt","Tracy King","Travis Clardy","Trent Ashby","Trey Martinez Fischer","Troy Fraser","Van Taylor","Wayne Faircloth","Wayne Smith","Will Hurd","Will Metcalf","Yvonne Davis"]

#error with Dan Patrick so fixed, and restarting with him!
#entitieslist = ["Dan Patrick","David Newell","David Porter","David Simpson","Dawnna Dukes","DeWayne Burns","Debbie Riddle","Debra Lehrmann","Dennis Bonnen","Dennis Paul","Diego Bernal","Don Huffines","Don Willett","Donna Campbell","Donna Howard","Doug Miller","Drew Darby","Drew Springer","Dustin Burrows","Dwayne Bohac","Ed Thompson","Eddie Johnson","Eddie Lucio III","Eddie Lucio Jr","Eddie Rodriguez","Elliott Naishtat","Elsa Alcala","Eric Johnson","Eva Guzman","Filemon Vela","Four Price","Garnet Coleman","Gary Elkins","Gary VanDeaver","Geanie Morrison","Gene Green","Gene Wu","George P. Bush","Gilbert Pena","Giovanni Capriglione","Glenn Hegar","Greg Bonnen","Harold Dutton","Helen Giddings","Henry Cuellar","Hubert Vo","Ina Minjarez","J. M. Lozano","J.D. Sheffield","James Frank","James White","Jane Nelson","Jason Isaac","Jason Villalba","Jeb Hensarling","Jeff Brown","Jeff Leach","Jeffrey Boyd","Jessica Farrar","Jim Keffer","Jim Murphy","Jimmie Don Aycock","Joan Huffman","Joaquin Castro","Jodie Laubenberg","Joe Barton","Joe Deshotel","Joe Farias","Joe Pickett","Joe Straus","John Carter","John Cornyn","John Culberson","John Cyrier","John Devine","John Frullo","John Kuempel","John Otto","John Raney","John Ratcliffe","John Smithee","John Whitmire","John Wray","John Zerwas","Jonathan Stickland","Jose Menendez","Jose Rodriguez","Joseph Moody","Juan Hinojosa","Judith Zaffirini","Justin Rodriguez","Kay Granger","Kel Seliger","Kelly Hancock","Ken King","Ken Paxton","Kenneth Sheets","Kenny Marchant","Kevin Brady","Kevin Eltife","Kevin Yeary","Kirk Watson","Konni Burton","Kyle Kacal","Lamar Smith","Larry Gonzales","Larry Phillips","Larry Taylor","Lawrence Meyers","Leighton Schubert","Linda Koop","Lloyd Doggett","Lois Kolkhorst","Louie Gohmert","Lyle Larson","Mac Thornberry","Marc Veasey","Marisa Marquez","Mark Keough","Marsha Farney","Mary Gonzalez","Matt Krause","Matt Rinaldi","Matt Schaefer","Matt Shaheen","Michael Burgess","Michael Keasler","Michael McCaul","Mike Conaway","Mike Schofield","Molly White","Morgan Meyer","Myra Crownover","Nathan Hecht","Nicole Collier","Oscar Longoria","Pat Fallon","Patricia Harless","Paul Bettencourt","Paul Green","Paul Workman","Pete Olson","Pete Sessions","Phil Johnson","Phil King","Phil Stephenson","Poncho Nevarez","Rafael Anchia","Ramon Romero","Randy Neugebauer","Randy Weber","Rene Oliveira","Richard Raymond","Rick Galindo","Rick Miller","Robert Nichols","Roberto Alonzo","Rodney Anderson","Rodney Ellis","Roger Williams","Roland Gutierrez","Ron Reynolds","Ron Simmons","Royce West","Ruben Hinojosa","Ruth Jones McClendon","Ryan Guillen","Ryan Sitton","Sam Johnson","Sarah Davis","Scott Sanford","Scott Turner","Senfronia Thompson","Sergio Munoz","Sharon Keller","Sheila Jackson Lee","Sid Miller","Stephanie Klick","Stuart Spitzer","Susan King","Sylvester Turner","Sylvia Garcia","Tan Parker","Ted Poe","Terry Canales","Todd Hunter","Toni Rose","Tony Dale","Tony Tinderholt","Tracy King","Travis Clardy","Trent Ashby","Trey Martinez Fischer","Troy Fraser","Van Taylor","Wayne Faircloth","Wayne Smith","Will Hurd","Will Metcalf","Yvonne Davis"]

#error with Hubert Vo so fix and restart
#entitieslist = ["Hubert Vo","Ina Minjarez","J. M. Lozano","J.D. Sheffield","James Frank","James White","Jane Nelson","Jason Isaac","Jason Villalba","Jeb Hensarling","Jeff Brown","Jeff Leach","Jeffrey Boyd","Jessica Farrar","Jim Keffer","Jim Murphy","Jimmie Don Aycock","Joan Huffman","Joaquin Castro","Jodie Laubenberg","Joe Barton","Joe Deshotel","Joe Farias","Joe Pickett","Joe Straus","John Carter","John Cornyn","John Culberson","John Cyrier","John Devine","John Frullo","John Kuempel","John Otto","John Raney","John Ratcliffe","John Smithee","John Whitmire","John Wray","John Zerwas","Jonathan Stickland","Jose Menendez","Jose Rodriguez","Joseph Moody","Juan Hinojosa","Judith Zaffirini","Justin Rodriguez","Kay Granger","Kel Seliger","Kelly Hancock","Ken King","Ken Paxton","Kenneth Sheets","Kenny Marchant","Kevin Brady","Kevin Eltife","Kevin Yeary","Kirk Watson","Konni Burton","Kyle Kacal","Lamar Smith","Larry Gonzales","Larry Phillips","Larry Taylor","Lawrence Meyers","Leighton Schubert","Linda Koop","Lloyd Doggett","Lois Kolkhorst","Louie Gohmert","Lyle Larson","Mac Thornberry","Marc Veasey","Marisa Marquez","Mark Keough","Marsha Farney","Mary Gonzalez","Matt Krause","Matt Rinaldi","Matt Schaefer","Matt Shaheen","Michael Burgess","Michael Keasler","Michael McCaul","Mike Conaway","Mike Schofield","Molly White","Morgan Meyer","Myra Crownover","Nathan Hecht","Nicole Collier","Oscar Longoria","Pat Fallon","Patricia Harless","Paul Bettencourt","Paul Green","Paul Workman","Pete Olson","Pete Sessions","Phil Johnson","Phil King","Phil Stephenson","Poncho Nevarez","Rafael Anchia","Ramon Romero","Randy Neugebauer","Randy Weber","Rene Oliveira","Richard Raymond","Rick Galindo","Rick Miller","Robert Nichols","Roberto Alonzo","Rodney Anderson","Rodney Ellis","Roger Williams","Roland Gutierrez","Ron Reynolds","Ron Simmons","Royce West","Ruben Hinojosa","Ruth Jones McClendon","Ryan Guillen","Ryan Sitton","Sam Johnson","Sarah Davis","Scott Sanford","Scott Turner","Senfronia Thompson","Sergio Munoz","Sharon Keller","Sheila Jackson Lee","Sid Miller","Stephanie Klick","Stuart Spitzer","Susan King","Sylvester Turner","Sylvia Garcia","Tan Parker","Ted Poe","Terry Canales","Todd Hunter","Toni Rose","Tony Dale","Tony Tinderholt","Tracy King","Travis Clardy","Trent Ashby","Trey Martinez Fischer","Troy Fraser","Van Taylor","Wayne Faircloth","Wayne Smith","Will Hurd","Will Metcalf","Yvonne Davis"]

#error with Jeb so fix and restart
#entitieslist = ["Jeb Hensarling","Jeff Brown","Jeff Leach","Jeffrey Boyd","Jessica Farrar","Jim Keffer","Jim Murphy","Jimmie Don Aycock","Joan Huffman","Joaquin Castro","Jodie Laubenberg","Joe Barton","Joe Deshotel","Joe Farias","Joe Pickett","Joe Straus","John Carter","John Cornyn","John Culberson","John Cyrier","John Devine","John Frullo","John Kuempel","John Otto","John Raney","John Ratcliffe","John Smithee","John Whitmire","John Wray","John Zerwas","Jonathan Stickland","Jose Menendez","Jose Rodriguez","Joseph Moody","Juan Hinojosa","Judith Zaffirini","Justin Rodriguez","Kay Granger","Kel Seliger","Kelly Hancock","Ken King","Ken Paxton","Kenneth Sheets","Kenny Marchant","Kevin Brady","Kevin Eltife","Kevin Yeary","Kirk Watson","Konni Burton","Kyle Kacal","Lamar Smith","Larry Gonzales","Larry Phillips","Larry Taylor","Lawrence Meyers","Leighton Schubert","Linda Koop","Lloyd Doggett","Lois Kolkhorst","Louie Gohmert","Lyle Larson","Mac Thornberry","Marc Veasey","Marisa Marquez","Mark Keough","Marsha Farney","Mary Gonzalez","Matt Krause","Matt Rinaldi","Matt Schaefer","Matt Shaheen","Michael Burgess","Michael Keasler","Michael McCaul","Mike Conaway","Mike Schofield","Molly White","Morgan Meyer","Myra Crownover","Nathan Hecht","Nicole Collier","Oscar Longoria","Pat Fallon","Patricia Harless","Paul Bettencourt","Paul Green","Paul Workman","Pete Olson","Pete Sessions","Phil Johnson","Phil King","Phil Stephenson","Poncho Nevarez","Rafael Anchia","Ramon Romero","Randy Neugebauer","Randy Weber","Rene Oliveira","Richard Raymond","Rick Galindo","Rick Miller","Robert Nichols","Roberto Alonzo","Rodney Anderson","Rodney Ellis","Roger Williams","Roland Gutierrez","Ron Reynolds","Ron Simmons","Royce West","Ruben Hinojosa","Ruth Jones McClendon","Ryan Guillen","Ryan Sitton","Sam Johnson","Sarah Davis","Scott Sanford","Scott Turner","Senfronia Thompson","Sergio Munoz","Sharon Keller","Sheila Jackson Lee","Sid Miller","Stephanie Klick","Stuart Spitzer","Susan King","Sylvester Turner","Sylvia Garcia","Tan Parker","Ted Poe","Terry Canales","Todd Hunter","Toni Rose","Tony Dale","Tony Tinderholt","Tracy King","Travis Clardy","Trent Ashby","Trey Martinez Fischer","Troy Fraser","Van Taylor","Wayne Faircloth","Wayne Smith","Will Hurd","Will Metcalf","Yvonne Davis"]

#now get three you are missing.. Ted Cruz, Tom Craddick, and Greg Abbott
#entitieslist = ["Greg Abbott", "Ted Cruz", "Tom Craddick"]

#csv headers

# "Austin American Statesman", "DALLAS MORNING NEWS", "HOUSTON CHRONICLE", "New York Times", "TEXAS OBSERVER", "Texas Tribune"
# [succart,skipart,sporart,dupeart,emptart,notfart,listart]:
# "name,succeed,skipped,

print("name,succeeded,skipped,aas_succeed, aas_skip, aas_sport, aas_dupe, aas_empty, aas_notfound, aas_list, DMNsucceed, DMNskip, DMNsport, DMNdupe, DMNempty, DMNnotfound, DMNlist, hc_succeed, hc_skip, hc_sport, hc_dupe, hc_empty, hc_notfound, hc_list, nyt_succeed, nyt_skip, nyt_sport, nyt_dupe, nyt_empty, nyt_notfound, nyt_list, txob_succeed, txob_skip, txob_sport, txob_dupe, txob_empty, txob_notfound, txob_list, txtr_succeed, txtr_skip, txtr_sport, txtr_dupe, txtr_empty, txtr_notfound, txtr_list")

debug = False
for name in entitieslist: 
	artstart = time.clock()
	
	#name = "Eddie Rodriguez"
	#print("PROCESSING: "+name)
	results = db.texnews.english.find({"entity":name},timeout=False)

	texts = {}
	local_urls_seen = {}
	skipped = 0
	#db.texnews.english.distinct("news-source").sort()
	succart = { "Austin American Statesman":0, "DALLAS MORNING NEWS":0, "HOUSTON CHRONICLE":0, "New York Times":0, "TEXAS OBSERVER":0, "Texas Tribune":0 }
	skipart = { "Austin American Statesman":0, "DALLAS MORNING NEWS":0, "HOUSTON CHRONICLE":0, "New York Times":0, "TEXAS OBSERVER":0, "Texas Tribune":0 }

	listart = { "Austin American Statesman":0, "DALLAS MORNING NEWS":0, "HOUSTON CHRONICLE":0, "New York Times":0, "TEXAS OBSERVER":0, "Texas Tribune":0 }
	sporart = { "Austin American Statesman":0, "DALLAS MORNING NEWS":0, "HOUSTON CHRONICLE":0, "New York Times":0, "TEXAS OBSERVER":0, "Texas Tribune":0 }
	dupeart = { "Austin American Statesman":0, "DALLAS MORNING NEWS":0, "HOUSTON CHRONICLE":0, "New York Times":0, "TEXAS OBSERVER":0, "Texas Tribune":0 }
	emptart = { "Austin American Statesman":0, "DALLAS MORNING NEWS":0, "HOUSTON CHRONICLE":0, "New York Times":0, "TEXAS OBSERVER":0, "Texas Tribune":0 }
	notfart = { "Austin American Statesman":0, "DALLAS MORNING NEWS":0, "HOUSTON CHRONICLE":0, "New York Times":0, "TEXAS OBSERVER":0, "Texas Tribune":0 }


	for a,art in enumerate(results):
	    if a > -1:
		if "/sports/" in art["url"]:
		    skipped += 1
		    skipart[art['news-source']] += 1
		    sporart[art['news-source']] += 1
		    continue
	
		#look for dupes
		if art["url"] in local_urls_seen:
			#printflush("\n ALREADY HANDLED THIS ARTICLE AT INDEX: "+str(local_urls_seen[art["url"]])+" SO SKIP IT")
			skipped += 1
		    	skipart[art['news-source']] += 1
		    	dupeart[art['news-source']] += 1
			continue
		else:		
			local_urls_seen[art["url"]] = a

		success,art = handle_date(art)
		if 'body' not in art and 'text' in art:
			art['body'] = art['text']
			del art['text']

		if art['body'] == "":
			skipped += 1
		    	skipart[art['news-source']] += 1
		    	emptart[art['news-source']] += 1
			continue

		sentences = get_article_sentences(art)
		arts = "\n".join(sentences)
		try:
			tt = arts.lower().translate({ord(c): None for c in string.punctuation})
		except:	
			print art
			print sentences
			traceback.print_exc(file=sys.stdout)
			print arts
			sys.exit()

		narts = tt.encode('ascii','ignore').replace("\n"," ")

		#sents = {'abstract': narts, 'title':art['title']}    #for use with python solution!
		#texts[a] = "\n".join(sents)

		title = art['title'].encode('ascii','ignore').replace("\n"," ")
		sents = {'text': narts, 'url':art['url'], 'title':title, 'news-source':art['news-source'], 'date': art['date'], 'language': art['language']}    #for use to write to file for R solution
		
		#before joining make sure we aren't adding a list!!
		entities, sentences = get_named_entities_per_sentence(sentences,debug) #dama_ner.py
		entities, found = verify_entity_found(entities,name,debug) 
		if found == False:
			skipped += 1
		    	skipart[art['news-source']] += 1
		    	notfart[art['news-source']] += 1
			continue
		dis_entities = disambiguate_entities(entities,sentences,db,debug) #debug
		dis_entities = filter_entities(dis_entities,name,debug)
		dcount = 0
		for d in dis_entities: dcount = dcount + len(dis_entities[d])
		if len(sentences) == 0: ratio = 0
		else: ratio = round(float(dcount)/len(sentences),2)
		if ratio > 10 or ratio == 0 :
			skipped +=1 
		    	skipart[art['news-source']] += 1
		    	listart[art['news-source']] += 1
			continue
		
		texts[a] = sents
		succart[art['news-source']] += 1


	dbtexts = texts
	#print("-----Articles Used:" + str(len(dbtexts.keys())))
	#print("-----Articles Skipped:" + str(skipped))
	
	toprint = name+","+str(len(dbtexts.keys()))+","+str(skipped)+","
	for src in [ "Austin American Statesman", "DALLAS MORNING NEWS", "HOUSTON CHRONICLE", "New York Times", "TEXAS OBSERVER", "Texas Tribune"]:
		for obj in [succart,skipart,sporart,dupeart,emptart,notfart,listart]:
			toprint += str(obj[src]) + ","
	print toprint


	#WRITE OUT TO FILE as a tsv
	'''
	topline = "title\tdate\tsource\turl\tlanguage\ttext\n"
	for i in texts:
		a = texts[i]	
		topline += a['title']+"\t"+a['date']+"\t"+a['news-source']+"\t"+a['url']+"\t"+a['language']+"\t"+a['text']+"\n"

	fname = name.lower().replace(" ","_") + "-articles.tsv"
	with open("data/tsvs/"+fname,'wb') as tsvfile:
		tsvfile.write(topline)
	'''
	
	
	artend = time.clock()
	#print("-----TIME TO PROCESS:" + str(artend - artstart) + " seconds")
	#print("")

sys.exit()


'''
#FROM HERE IS IF YOU WANT TO DO TOPIC MODELING IN PYTHON BUT WE ARE USING R SOLUTION INSTEAD
sessions = texts


corpus = []
titles = []
for id, session in sorted(sessions.iteritems(), key=lambda t: int(t[0])):
    corpus.append(session["abstract"])
    titles.append(session["title"])




n_topics = 15
n_top_words = 50
n_features = 6000

# vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1,1), min_df = 0, stop_words = 'english')
vectorizer = CountVectorizer(analyzer='word', ngram_range=(1,1), min_df = 0, stop_words = 'english')
matrix =  vectorizer.fit_transform(corpus)
feature_names = vectorizer.get_feature_names()

import lda
import numpy as np

vocab = feature_names

model = lda.LDA(n_topics=20, n_iter=500, random_state=1)
model.fit(matrix)
topic_word = model.topic_word_
n_top_words = 20

for i, topic_dist in enumerate(topic_word):
    topic_words = np.array(vocab)[np.argsort(topic_dist)][:-n_top_words:-1]
    print('Topic {}: {}'.format(i, ' '.join(topic_words)))

doc_topic = model.doc_topic_
for i in range(0, len(titles)):
    print("{} (top topic: {})".format(titles[i], doc_topic[i].argmax()))
    print(doc_topic[i].argsort()[::-1][:3])

# with open("data/topics.csv", "w") as file:
#     writer = csv.writer(file, delimiter=",")
#     writer.writerow(["topicId", "word"])
#
#     for i, topic_dist in enumerate(topic_word):
#         topic_words = np.array(vocab)[np.argsort(topic_dist)][:-n_top_words:-1]
#         for topic_word in topic_words:
#             writer.writerow([i, topic_word])
#         print('Topic {}: {}'.format(i, ' '.join(topic_words)))
#
# with open("data/sessions-topics.csv", "w") as file:
#     writer = csv.writer(file, delimiter=",")
#     writer.writerow(["sessionId", "topicId"])
#
#     doc_topic = model.doc_topic_
#     for i in range(0, len(titles)):
#         writer.writerow([i, doc_topic[i].argmax()])
#         print("{} (top topic: {})".format(titles[i], doc_topic[i].argmax()))
#         print(doc_topic[i].argsort()[::-1][:3])
'''
