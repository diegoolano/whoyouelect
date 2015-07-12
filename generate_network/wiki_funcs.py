from dama_globals import *
from dama_utils import *   #for db
import sys
import requests
from bs4 import BeautifulSoup
 
def get_wiki_link(person):
	ret = ""
	#return ret

	#try local db of wikiandphotos first and if not call wikipedia.org
	conn = MongoClient()
	db = conn.newsdb
	rr = db.texnews.wikiandphotos.find({"full_name" : person})
	if rr.count() == 1:
		for r in rr:
			if r["wiki_stub"] != "":
				ret = r["wiki_stub"]
				break
	else:
		try:
			URL = "http://www.wikipedia.org/search-redirect.php?family=wikipedia&search=%s&language=en"        
			person = person.replace(" ","%20")
			print "call wiki_link url for "+ person
		
			data = requests.get(URL % person )        
			soup = BeautifulSoup(data.content)
			head = soup.find("head")    #get canonical
			lnk = head.find("link",{'rel':'canonical'})
			ret = lnk.attrs['href']
			
			#TODO still gives Wikipedia disambiguation page for TSU, but fixes many of the 435!  look into this
		except:
			try:
				print("no wiki link found for "+person)
			except:
				print("couldn't even print out error cause person has weird character")

	return ret
    
def get_wiki_photo(person):
	ret = ""
	#return ret
	#try local db of wikiandphotos first and if not call wikipedia.org

	conn = MongoClient()
	db = conn.newsdb
	rr = db.texnews.wikiandphotos.find({"full_name" : person})
	if rr.count() == 1:
		for r in rr:
			if r["photo_url"] != "":
				ret = r["photo_url"]
				break
	else:
		try:
			URL = "http://en.wikipedia.org/w/api.php?action=query&titles=%s&prop=pageimages&format=json&pithumbsize=200"
			person = person.replace(" ","%20")
			print "call wiki_photo url for "+ person
			data = requests.get(URL % person ).json()
			images = data['query']['pages']
			ret = images[images.keys()[0]]["thumbnail"]["source"]
		except:
			print("no wiki photo found for "+person)
	return ret

#How to get position:
#this gets a person's job position [politician, etc]
def get_wiki_des(person):
    ret = ""
    try:
        URL = "http://en.wikipedia.org/w/api.php?action=query&titles=%s&prop=pageterms&format=json&pithumbsize=200"
        person = person.replace(" ","%20")
        data = requests.get(URL % person ).json()
        d = data["query"]["pages"]
        terms = d[d.keys()[0]]['terms']
        #terms contains "alias" which is good, but also "description"
        ret = terms["description"][0]
    except:
        print("no wiki description found for "+person)
        nothin = 1
    return ret

def get_wiki_shortbio(person):
    ret = ""
    #http://projects.knightlab.com/projects/metrovote
    try:
        person = person.replace(" ","%20")
        URL = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro=&explaintext=&titles=%s"
	print "Get Wiki ShortBio for "+person
        data = requests.get(URL % person ).json()
        d = data['query']['pages']
        wikilink = "http://en.wikipedia.org/wiki/"+person
        ret = [ d[d.keys()[0]]['extract'] , wikilink ]
    except:
        print("no wiki short bio found for "+person)
    return ret


#"politician" in "American businessman and politician"
#bio, link = get_wiki_shortbio("Garnet Coleman")


updebug = False
lookup=True
def update_politician(polname,photo_url="",position="",fullname=""):
    
    if updebug:
        printflush("In update politician with "+polname)
    try:
        gid = global_index[polname]
                                            
        if position != "":
            if updebug:
                printflush("Use passed in position: "+position)
            global_entities[gid]['position'] = [position]
            global_entities[gid]['entity_type'] = "politician"  #if position given, assume its a politician
        else:
            #if no position given, verify this person is a politician!
            if lookup:
                desc = get_wiki_des(polname)
                if desc != "":
                    if updebug:
                            printflush("Use found description: "+desc)
                            
                    if 'position' in global_entities[gid]:
                        global_entities[gid]['position'].append(desc)
                    else:
                        global_entities[gid]['position'] = [desc]
                        
                    if "politician" in desc or "President" in desc or "Governor" in desc or "Senator" in desc or "Attorney General" in desc or "legislator" in desc:
                        if updebug:
                            printflush("Labelling as politican")
                        global_entities[gid]['entity_type'] = "politician"
                        
            
        if photo_url != "":
            if updebug:
                printflush("Use passed in image: "+photo_url)
            global_entities[gid]['photo_url'] = photo_url
        else:
            if lookup:
                photo = get_wiki_photo(polname)
                if photo != "":
                    if updebug:
                            printflush("Use found image: "+photo)
                    global_entities[gid]['photo_url'] = photo
                    
        
        
        if fullname != "":
            global_entities[gid]['fullname'] = fullname
            
        
        if updebug:
            printflush(global_entities[gid])
    except:
        print "ERROR: "
	print sys.exc_info()[0]


#GARNET COLEMAN SPECIFIC HACK FIXES: TODO MAKE THIS GENERALIZABLE
def run_result_updates():
	update_politician("Rick Perry","http://s3.amazonaws.com/static.texastribune.org/media/profiles/politicians/Perry-Rick768_jpg_131x197_crop_q100.jpg")
	update_politician("Barack Obama","http://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/President_Barack_Obama.jpg/440px-President_Barack_Obama.jpg")
	update_politician("Bill White","http://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Bill_White.jpg/440px-Bill_White.jpg","Former Mayor Of Houston - 2004 - 2010")
	update_politician("Mayor-elect Annise Parker","http://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Annise_Parker.JPG/440px-Annise_Parker.JPG","Current Mayor Of Houston","Annise Parker")
	update_politician("Talmadge Heflin","http://www.greaterhpc.org/Images%20-%20Program/2007%20Program%20Images/070828%20-Talmadge%20Heflin.jpg","Former Texas Senator")
	update_politician("Rick Noriega","http://upload.wikimedia.org/wikipedia/commons/f/f7/Rick_Noriega_4.jpg","former Texas House of Representatives")
	update_politician("Ron Wilson","http://www.lrl.state.tx.us/scanned/members/photos/thumbnails/W/Wilson,-Ron.jpg","Former Texas Rep")
	update_politician("Sheila Jackson Lee","http://upload.wikimedia.org/wikipedia/commons/e/ef/SheilaJackson.JPG","U.S. Represenative of Texas")
	update_politician("George W. Bush","http://en.wikipedia.org/wiki/File:George-W-Bush.jpeg")
	update_politician("Kyle Janek","http://mikefalick.blogs.com/my_blog/images/2008/01/29/janek.jpg","Former Republican Rep") 
	update_politician("Tom DeLay","http://upload.wikimedia.org/wikipedia/commons/thumb/0/01/TomDeLay.jpg/400px-TomDeLay.jpg")
	update_politician("Kay Bailey Hutchison")
	update_politician("Ada Edwards","","Former Houston City Council Member")
	update_politician("Martha Wong","http://www.asianamerican.net/bios/photos/Wong-Martha.jpg")
	update_politician("Arlene Wohlgemuth","http://www.tha.org/HealthCareProviders/Education/C0BCTHAAnnualConfer0895/img/Arlene_Wohlgemuth_100.jpg") 
	update_politician("Brian McCall","http://www.tsus.edu/leadership/chancellor/brian-mccall/contentParagraph/0/content_files/file0/document/McCall_4_sm.jpg","chancellor of the Texas State University System")
	update_politician("Ray Hill","","political talk show host runs the Friday night Prison Show from KPFT")

	possible_pols = ["Chris Bell","Terral Smith","Greg Abbott","Lee Brown","Mickey Leland","Arthur Smith",
	"Kinky Friedman","Trish Wise","Carole Keeton Strayhorn","Herschel Smith","Jon Lindsay","Robert Talton",
	"Hillary Rodham Clinton","Charles Soechting","Gene Green","Andy Icken","Robert Gates","Al Gore",
	"Debra Danburg","Mark Jones","Bob Lanier","Joe Moreno","John Cornyn","Bill Callegari","Adrian Garcia",
	"Paul Ryan","Bill Clinton","David Lopez","Leo Vasquez","Albert Hawkins",
	"Marc Campos","Melissa Noriega","Ed Emmett","Bill Ratliff","Kevin Bailey","Al Bennett","Cheryl Armitige","Joe Nixon","Christina Cabral",
	"Joseph Carlos Madden","Andy Taylor","Gilbert Garcia","Gerald Birnberg","Pete Laney","Martin Coleman",
	"Sandra Lopez","Edward Kennedy","Anne Dunkelberg","Harold Hurtt","Gordon Quan","Ronald Green",
	"Craig Washington","Bob Perry","Carroll Robinson","Kathy Walt","Peter Brown","Glenn Lewis",
	"Belinda Griffin","El Franco Lee","John Rudley","Bill Miller","Leland Anthony Hall","Paul Broussard",
	"Eugene Antill","Mark Yudof","Steve Pittman","Arturo Michel","William Lawson","Fred Bosse","Danny Perkins",
	"Randall Ellis","Frank Wilson","Mark Ellis","Bill Davis","Jesse Jackson","Theola Petteway","Garry Mauro",
	"Ray Driscoll","Fred Hofheinz","Richard Frankoff","Robert Eckels","Alan Bernstein","Sylvia Brooks",
	"Rob Junell","Steve Radack","Jared Woodfill","Mitt Romney","May Walker","Charles Stuart","Fred Hill",
	"Kathy Hubbard","Manuel Rodriguez Jr","Ramiro Fonseca","Mark A. Wallace","Pat Pound","Seor Morales",
	"Glenn Neal","Phillip Martin","Jack E. Pratt Sr","Susan F. Zinn","Jessica Siegel","Tracy Gilbert",
	"Linda Bridges","Drayton McLane","Talton Craddick","George Zimmerman","Bill Calderon","Monte Jones",
	"Ryan Goodland","George Wallace","Alfred Gilman","Keith Wade","Eduardo Sanchez","Jay Gogue",
	"Stephanie Goodman","Grant Martin","Alain Lee","Don Gilbert","Eastwood Scott","Joe Turner","Tom Schieffer",
	"David Bernsen","Ana E. Hernandez","J. Timothy Boddie Jr","Josh Havens","George Hammerlein","Howard Dean",
	"Ron Kirk","Mike Garver","Susan Combs","Chet Edwards","Kathy Whitmire","Bob McNair","Clay Robison",
	"Richard Murray","Tom Suehs","Gary Bledsoe","Raymund Paredes","Corbin Van Arsdale","LaRhonda Torry","Peggy Hamric"]

	for p in possible_pols:
	    update_politician(p)

	global_entities[global_index["Chris Bell"]]["position"] = ["Member of the U.S. House of Representatives from Texas's 25th district"]
	global_entities[global_index["Chris Bell"]]["entity_type"] = "politician"
	global_entities[global_index["Greg Abbott"]]["entity_type"] = "politician"
	global_entities[global_index["Brian McCall"]]["entity_type"] = "politician"
	global_entities[global_index["Brian McCall"]]["position"] = ["Representative"]
	global_entities[global_index["Lee Brown"]]["entity_type"] = "politician"
	global_entities[global_index["Lee Brown"]]["position"] = ["Former Mayor of Houston"]
	global_entities[global_index["Lee Brown"]]["photo_url"] = "http://www.projectblackman.com/images/NotablePeople/LeePBrown1.jpg"
	global_entities[global_index["Herschel Smith"]]["entity_type"] = "politician"
	global_entities[global_index["Herschel Smith"]]["position"] = ["lost Democratic Primary for Texas House District 147 in 2006"]
	global_entities[global_index["Charles Soechting"]]["entity_type"] = "politician"
	global_entities[global_index["Charles Soechting"]]["position"] = ["State Democratic Chairman", "Lawyer"]
	global_entities[global_index["Andy Icken"]]["entity_type"] = "politician"
	global_entities[global_index["Andy Icken"]]["position"] = ["Chief Development Officer for the City of Houston"]
	global_entities[global_index["Robert Gates"]]["entity_type"] = "politician"
	global_entities[global_index["Al Gore"]]["entity_type"] = "politician"
	#
	global_entities[global_index["Debra Danburg"]]["entity_type"] = "politician"
	global_entities[global_index["Debra Danburg"]]["position"] = ["Former Representative"]
	#
	global_entities[global_index["Mark Jones"]]["position"] = ["Fellow in political science at the Baker Institute and the Joseph D. Jamail Chair in Latin American Studies at Rice University"]
	#
	global_entities[global_index["Bob Lanier"]]["entity_type"] = "politician"
	global_entities[global_index["Bob Lanier"]]["photo_url"] = "http://upload.wikimedia.org/wikipedia/commons/thumb/c/c6/Bob_Lanier_Portrait.jpg/440px-Bob_Lanier_Portrait.jpg"
	global_entities[global_index["Bob Lanier"]]["position"] = ["Former Mayor of the city of Houston, Texas from 1992 to 1998"]
	#
	global_entities[global_index["Joe Moreno"]]["entity_type"] = "politician"
	global_entities[global_index["Joe Moreno"]]["location"] = "Houston"
	global_entities[global_index["Joe Moreno"]]["position"] = ["Former Representative"]
	#
	global_entities[global_index["John Cornyn"]]["entity_type"] = "politician"
	#
	global_entities[global_index["Bill Callegari"]]["entity_type"] = "politician"
	#
	global_entities[global_index["Adrian Garcia"]]["entity_type"] = "politician"
	global_entities[global_index["Adrian Garcia"]]["position"] = ["the Sheriff of Harris County"]
	global_entities[global_index["Adrian Garcia"]]["photo_url"] = "http://blog.chron.com/txpotomac/files/2011/07/sheriff-adrian-garcia.jpg"
	#
	global_entities[global_index["Leo Vasquez"]]["entity_type"] = "politician"
	global_entities[global_index["Leo Vasquez"]]["position"] = ["Harris County Tax Assessor Collector"]
	#
	global_entities[global_index["Albert Hawkins"]]["entity_type"] = "politician"
	global_entities[global_index["Albert Hawkins"]]["position"] = ["Former commissioner of the Health and Human Services Commission"]

	global_entities[global_index["Marc Campos"]]["entity_type"] = "politician"
	global_entities[global_index["Marc Campos"]]["position"] = ["Political Consultant"]

	global_entities[global_index["Kevin Bailey"]]["entity_type"] = "politician"
	global_entities[global_index["Kevin Bailey"]]["position"] = ["Texas House of Representatives representing the 140th District in Houston, Texas from 1991 through 2008"]

	global_entities[global_index["Al Bennett"]]["entity_type"] = "politician"
	global_entities[global_index["Al Bennett"]]["position"] = ["judge"]

	global_entities[global_index["Joe Nixon"]]["entity_type"] = "politician"

	#http://www.texastribune.org/directory/joseph-carlos-madden/
	global_entities[global_index["Joseph Carlos Madden"]]["entity_type"] = "politician"
	global_entities[global_index["Joseph Carlos Madden"]]['position'] = ["Lost Eleection For Texas House District 137, 2012-05-29"] 

	global_entities[global_index["Pete Laney"]]['position'] = ["Speaker", "American politician"]

	global_entities[global_index["Martin Coleman"]]['position'] = []
	    
	global_entities[global_index["Edward Kennedy"]]["entity_type"] = "politician"
	global_entities[global_index["Edward Kennedy"]]["photo_url"] = "http://media.washingtonpost.com/wp-srv/politics/congress/members/photos/228/K000105.jpg"

	global_entities[global_index["Anne Dunkelberg"]]["position"] = ["Associate Director, Health and Wellness Program Director of The Center for Public Policy Priorities"]

	global_entities[global_index["Harold Hurtt"]]["position"] = ['American police chief']
	global_entities[global_index["Gordon Quan"]]["position"] = ['American politician']
	     
	global_entities[global_index["Ronald Green"]]["entity_type"] = "politician"
	global_entities[global_index["Ronald Green"]]["position"] = ["Houston City Controller"]
			
	global_entities[global_index["Craig Washington"]]["position"] = ["Representative"]
			
	global_entities[global_index["Bob Perry"]]["position"] = ["Houston, Texas homebuilder, owner of Perry Homes, and major contributor to a number of politically oriented 527 groups, such as the Swift Vets and POWs for Truth and the Economic Freedom Fund"]

	global_entities[global_index["Kathy Walt"]]["entity_type"] = "politician"                
	global_entities[global_index["Kathy Walt"]]["position"] = ["Chief of staff for Rick Perry"]

	global_entities[global_index["Peter Brown"]]["entity_type"] = "politician"                                
	global_entities[global_index["Peter Brown"]]["position"] = ["a politician who held office as an at-large Council Member in the city of Houston"]

	global_entities[global_index["Glenn Lewis"]]["entity_type"] = "politician"                 
	global_entities[global_index["Glenn Lewis"]]["position"] = ["Former Texas House Representative"]                
	global_entities[global_index["Glenn Lewis"]]["photo_url"] = "https://txdirectory.com/files/photo/per29091.jpg"
					
	global_entities[global_index["Belinda Griffin"]]["position"] = ["TSU Regents chairwoman"]

	global_entities[global_index["El Franco Lee"]]["entity_type"] = "politician"                
	global_entities[global_index["El Franco Lee"]]["position"] = ["Harris County Commissioner"]
	 
	global_entities[global_index["Bill Miller"]]["position"] =  ["political consultant and founding partner in HillCo Partners LLC, an Austin lobby firm formed in 1998"]
			
	global_entities[global_index['David Dewhurst']]["photo_url"] = "http://juanitajean.com/wp-content/uploads/2011/05/dewhurst-david_.jpg"
