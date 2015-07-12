#import nltk    #look for exec popup (go app tabs) , download reuters, oanc_masc, conll2002, couldn't find senna data

#for senna, this http://brenocon.com/blog/2011/09/end-to-end-nlp-packages/   lead me to this
#http://ml.nec-labs.com/senna/  and then http://ml.nec-labs.com/senna/download.html
#installed in ~/Downloads/senna/senna-osx

import nltk
#print nltk.__version__
#from nltk.tag import SennaNERTagger
#print nltk.__path__
#nltk.download()      #downloaded to /Users/dolano/nltk_data


#import nltk
#https://gist.github.com/onyxfish/322906

def extract_entity_names(t):
    entity_names = []
    
    if hasattr(t, 'label') and t.label:
        if t.label() == 'NE':
            entity_names.append(' '.join([child[0] for child in t]))
        else:
            for child in t:
                entity_names.extend(extract_entity_names(child))
                
    return entity_names

def show_entities_with_plain_nltk(sentences):
    print("\n with plain nltk: ")
    #sentences = nltk.sent_tokenize(sample)
    tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
    tagged_sentences = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]
    chunked_sentences = nltk.ne_chunk_sents(tagged_sentences, binary=True)
    entity_names = []
    for tree in chunked_sentences:
        # Print results per sentence
        # print extract_entity_names(tree)    
        entity_names.extend(extract_entity_names(tree))

    # Print all entity names
    #print entity_names

    # Print unique entity names
    print sorted(set(entity_names))


# In[101]:

url = "http://www.chron.com/news/houston-texas/article/Speaker-names-leaders-for-key-House-committees-1733399.php"
sents = url_texts[url]
from nltk.tag.stanford import NERTagger
nerpath = "/Users/dolano/htdocs/dama-larca/stanford-ner/stanford-ner-2015-01-30/"
st = NERTagger(nerpath+"classifiers/english.conll.4class.distsim.crf.ser.gz", nerpath+'stanford-ner.jar')
tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sents]


# In[126]:

#tagged_sentences = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]
#tagged_sentences = [st.tag(sentence) for sentence in tokenized_sentences]
def extract_entity_names_two(t):
    entity_names = []
    print "##################################in extract"
    #print t
    if hasattr(t, 'label') and t.label or len(t) == 2:
        if len(t)==2:
            label = t[1]
        else:
            label = t.label()
            
        if label in ["PERSON","LOCATION","MISC","ORGANIZATION"]:
            print "YES"
            #print "t label()"
            #print label
            if len(t) == 2:
                entity_names.append(t[0])
            else:
                entity_names.append(' '.join([child[0] for child in t]))
        else:
            #print "nope"
            for child in t:
                #print child
                entity_names.extend(extract_entity_names_two(child))
                
    return entity_names

tagged_sentences = []
for sentence in tokenized_sentences:
    cleanedsentence = [s.replace(u'\u2022','') for s in sentence]
    tmp = st.tag(cleanedsentence)
    #print tmp
    tagged_sentences.append(tmp)
    
#print tagged_sentences
chunked_sentences = nltk.ne_chunk_sents(tagged_sentences)#, binary=True)
entity_names = []
save = []
count = 0
for tree in chunked_sentences:
    print "******************************in main"
    print tree
    save.append(tree)
    count = count + 1
    entity_names.extend(extract_entity_names_two(tree))
    

# Print unique entity names
print sorted(set(entity_names))


#len(save)


#TODO before excluding have a way to look up how well our entity detection is doing per article somehow
#global_entities = []
#global_relations = {}
#article_relations = {}
#global_index = {}
#json_output = {"elements":{"nodes":[],"edges":[]}}
#edges_seen = []      #just used to see whether an edge has already been added
#text_snippets = []   #keeps track of text snippets
#entity_edges = {}

should_see = {}   #url dict to keep hand made guide of what entities should have been found 

#pingar, apache stanbol, mitie, stanford entity detection

#apache stanbol
#http://www.slideshare.net/valexiev1/comparing-ontotext-kim-and-apache-stanbol   ..   not good, but this is 4 years old
#https://stanbol.apache.org/docs/trunk/components/enhancer/engines/opencalaisengine.html
#https://stanbol.apache.org/docs/0.9.0-incubating/enhancer/engines/namedentityextractionengine.html

#pingar
#http://apidemo.pingar.com/Entities.aspx#wrapper   .. not super impressive 
#http://www.slideshare.net/PingarHQ/case-study-text-analytics-on-2-million-documents


#stanford named entity recognizer
#nlp.stanford.edu/software/CRF-NER.shtml
#http://nlp.stanford.edu:8080/ner/process   with english.conll.4class.distsim.crf.ser.gz  GIVES GOOD RESULTS.. try!

#illinois named entity recognizer
#LOOK INTO THIS: http://cogcomp.cs.illinois.edu/index.html  ,, specifically 2014 tools doc
#http://cogcomp.cs.illinois.edu/page/software/
#HTML TAG STRIPPER: http://cogcomp.cs.illinois.edu/page/tools_view/7  (good for incorporating new links!)
#Named Entity: http://cogcomp.cs.illinois.edu/page/software_view/NETagger


#dbpedia spotlight ... hmmm..
#http://dbpedia-spotlight.github.io/demo/
#https://github.com/dbpedia-spotlight/dbpedia-spotlight/wiki
#http://stackoverflow.com/questions/20796266/named-entity-recognition-using-freebase  <-- PRETTY GOOD


#QUESTIONS/PAPERS:
#http://www.quora.com/How-accurate-are-entity-extraction-tools
#http://arxiv.org/pdf/1308.0661.pdf (comparing Stanford NER, Illinois NET, OpenCalais NER WS and Alias-i LingPipe)




#1.
#"http://www.chron.com/news/houston-texas/article/Speaker-names-leaders-for-key-House-committees-1733399.php"
#   for this one, after R-CARLTON there is a colon followed by entity
#for GC missed: Calendars Committee, County Affairs, Public Health
#for others: Speaker pro tempore, Hurricane Ike, State Affairs, Calendars, Regulated Industries Committee, Public Education
#Energy Resources and State Affairs found, but should be Energy Resources ,    and State Affairs ( which itself appears twice before)

#2.
#http://www.chron.com/news/houston-texas/article/TSU-report-blasts-governing-board-1798853.php
#Glen Lewis not found because his mention was not in a <p> 

#3.
#http://www.chron.com/neighborhood/heights-news/article/Poll-shows-blacks-concerned-1554258.php
#found Katrina in "hurricanes Katrina and Rita"
#missed School of Public Affairs (though found Barbara Jordan/Mickey Leland School of Public Affairs)
#missed Third Ward, Hurricane Katrina, Hurricane Rita

#4.
#http://www.chron.com/opinion/editorials/article/It-s-city-business-6036503.php
#missed 84th Legislative session,  Houston Firefighter Pension System (found Houston)
#missed [Council Member Michael] Kubosh (instead found Michael])    <-- if you find [] before an entity try to include it
#missed Houston Firefighter's Relief and Retirement Fund
#found Deferred Retirement Option Plan.. from Deferred Retirement Option Plan (DROP)  .. maybe include (DROP) as alias

#from nltk.tag.senna import NERTagger   #this works for senna
#from nltk.tag import SennaNERTagger    #this doesn't
from nltk.tag.stanford import NERTagger #this works for stanford

def try_with_nltk(u):
    printflush("in nltk with "+u+"\n")
    sentences = url_texts[u]
    #Diegos-MacBook-Pro:ivan dolano$ locate nltk | grep senna
    #/Users/dolano/anaconda/lib/python2.7/site-packages/nltk/tag/senna.py
    #/Users/dolano/anaconda/lib/python2.7/site-packages/nltk-3.0.0-py2.7.egg/nltk/tag/senna.py
    #/Users/dolano/anaconda/pkgs/nltk-2.0.4-np18py27_0/lib/python2.7/site-packages/nltk/tag/senna.py
    #/anaconda/lib/python2.7/site-packages/nltk/tag/senna.py
    #/anaconda/pkgs/nltk-2.0.4-np18py27_0/lib/python2.7/site-packages/nltk/tag/senna.py
    
    #so I don't have the data i need so install it
    #http://www.nltk.org/data.html
    #reuters, oanc_masc, conll2002, couldn't find senna data , downloaded to /Users/dolano/nltk_data
    
    #nertagger = NERTagger('/usr/share/senna-v2.0')
    #nertagger = NERTagger('/Users/dolano/Downloads/senna')         #this works for senna
    #nertagger = SennaNERTagger('/Users/dolano/Downloads/senna')
    
    #nerpath = "/Users/dolano/htdocs/dama-larca/stanford-ner/stanford-ner-2015-01-30/"
    #nertagger = NERTagger(nerpath+"classifiers/english.all.3class.distsim.crf.ser.gz", nerpath+'stanford-ner.jar')
    
    nerpath = "/Users/dolano/htdocs/dama-larca/stanford-ner/stanford-ner-2015-01-30/"
    st = NERTagger(nerpath+"classifiers/english.conll.4class.distsim.crf.ser.gz", nerpath+'stanford-ner.jar')

    
    #nertagger.tag('Shakespeare theatre was in London .'.split())
    #nertagger.tag(sentences.split())
    
    i = 0
    if i == 1:
        for s in sentences:
            #print "For sentence:"+s+"\n"
            #print nertagger.tag(s.split())  #for senna
            tagged = st.tag(s.split())
            sent_entities = nltk.chunk.ne_chunk(tagged)
            if len(sent_entities) > 0:
                try:
                    es = [ se[0]+" - "+se[1] for se in sent_entities if len(se) == 2 and len(se[1]) ==1 and se[1] != "O"]
                    if len(es) > 0:
                        print ", ".join(es)                
                except:
                    print "error"                
                    print sent_entities
                    for se in sent_entities:
                        print len(se),se,se[0],se[1]
    else:
        tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
        #tagged_sentences = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]
        tagged_sentences = [st.tag(sentence) for sentence in tokenized_sentences]
        chunked_sentences = nltk.ne_chunk_sents(tagged_sentences, binary=True)
        entity_names = []
        for tree in chunked_sentences:
            entity_names.extend(extract_entity_names(tree))

        # Print unique entity names
        print sorted(set(entity_names))

def inspect_article_findings(u,show_article_text=False):
    these_sentences = url_texts[u]   #u is the url, url_texts[u] are the sentences in url
    these_ents = global_relations[u]['entities']  #entities found
    these_rels = global_relations[u]['relations'] #relations formed from entities
 
    print u
    if show_article_text:
        print ".  ".join(url_texts[u])+"\n"
        
    print "Entities FOUND:"
    for i,e in enumerate(sorted(these_ents.keys())):
        if 'position' in these_ents[e] and 'location' in these_ents[e] and 'party' in these_ents[e]:
            print "\t" + e + " - " + these_ents[e]['entity_type'] + " , " + ", ".join(these_ents[e]['position'])+" .. loc= "+these_ents[e]['location']+" .. party= "+these_ents[e]['party']
        else:
            print "\t" + e + " - " + these_ents[e]['entity_type'] 

    print "\n"
    print "Relations MADE:"
    for i in these_rels:
        if i['type'] != 'same article':
            print "\t"+ i['term1'] + " - "+ i['term2'] + ' : ' + i['type']
 
#len(global_relations) #1103

for i,u in enumerate(global_relations.keys()):
    if i == 1:
        inspect_article_findings(u,show_article_text=False)
        try_with_nltk(u)   #senna or stanford
        #show_entities_with_plain_nltk(url_texts[u])


# In[146]:

#ADD WIKI LINKS TO EXISTING NODES
import json
txsmr = open("/Users/dolano/htdocs/dama-larca/d3/mar25/smallnet-revised-march17.json")
datasmr = json.load(txsmr)


# In[205]:

ambigious = 0
for n in datasmr['elements']['nodes']:
    #des = get_wiki_des(n['full_name'])
    des = get_wiki_link(n['full_name'])
    if des == "Wikipedia disambiguation page" or des == "":
        if des == "":
            n['wiki_stub'] = "FIX: page not found"
        else:
            n['wiki_stub'] = "FIX: ambigious page"
        ambigious = ambigious + 1
    else:
        #n['wiki_stub'] = n['full_name'].replace(" ","_") #http://en.wikipedia.org/wiki/Texas_Southern_University
        n['wiki_stub'] = des
        
#I could make a google scraper to find these! ambigious ones (
#texas tribune texas site:en.wikipedia.org   
#THIS WILL WORK FOR MOST, but for some "CHIP" various are returned, and they are all wrong (thus label as such )



# In[203]:

#get_wiki_link("John Zerwas")


# In[206]:

#"Affordable Care Act".replace(" ","_")
print "Ambigious: ", ambigious
for n in datasmr['elements']['nodes']:
    print n['full_name'], n['wiki_stub']


# In[265]:

#ambigious   #435 now its out of 663, 350 which are "page not found" .. 85 which are ambigious
c= 0 
amb = []
for n in datasmr['elements']['nodes']:
    #if "Special:Search?" in n['wiki_stub']:
    if "NONE" in n['wiki_stub']:
        c = c + 1
        #n["wiki_stub"] = "NONE"
        if n["ballot_url"] == "":
            del n["ballot_url"]
            del n["ballot_desc"]
        else:
            n['wiki_stub'] = "BALLOT"
            amb.append(n["full_name"])
        #n["ballot_url"], n["ballot_desc"] = get_ballot_link(n['full_name'])
        #print n
        
    #if n['full_name'] == "TSU":
    #    print n

#print len(amb)       #24 PEOPLE WHO WERE NOT FOUND IN WIKIPEDIA BUT WERE FOUND IN BALLOTPEDIA 
#sorted(amb)



# In[276]:

c= 0 
amb = []
for n in datasmr['elements']['nodes']:
    if "NONE" in n['wiki_stub']:
        c = c + 1
        amb.append(n)
    if n['full_name'] == "Chris Bell":
        n['wiki_stub'] = "http://en.wikipedia.org/wiki/Chris_Bell_(politician)"
        

print len(amb)  #197 people neither in wiki or ballotpedia
for a in sorted(amb):
    print a
    
#http://www.lrl.state.tx.us/legis/BillSearch/searchresults.cfm?subjectList=BUFFALO%20BAYOU%20MANAGEMENT%20DISTRICT

#BILLS , http://openstates.org/tx/bills/83/HB3692/ or maybe
#        http://www.lrl.state.tx.us/legis/BillSearch/BillDetails.cfm?legSession=83-0&billTypeDetail=HB&billnumberDetail=3692&submitbutton=Search+by+bill
#YEAR/SESSION IS IMPORTANT 

#http://en.wikipedia.org/wiki/Children%27s_Defense_Fund for Children 's Defense Fund .. fix by fixing space issue
def fix_spacing_issue():
    for n in datasmr['elements']['nodes']:
        if "NONE" in n['wiki_stub'] and " 's" in n['full_name']:
            print "for "+n['full_name'].replace(" 's","'s")
            poslink = get_wiki_link(n['full_name'].replace(" 's","'s"))
            if "Special:Search?" in poslink:
                print "\tfound nothing"
            else:
                print "\tfound wiki: "+poslink
                n['wiki_stub'] = poslink


# In[277]:

print datasmr['elements']['nodes']


# In[ ]:

'''
{"TSU":"http://en.wikipedia.org/wiki/Texas_Southern_University",
 "Bill White":"http://en.wikipedia.org/wiki/Bill_White_(Texas_politician)"
 "John Zerwas":"John_M._Zerwas",
 "Montrose":"Montrose,_Houston",
 "CHIP":"State_Children%27s_Health_Insurance_Program",
 "Texas Tribune":"The_Texas_Tribune",
 "UH":"University_of_Houston",
 "A&M":"Texas_A%26M_University",
 "John B. Coleman":"none",
 "Ron Wilson":"none",
 "Fourth Ward":"Fourth_Ward,_Houston",
 "Third Ward":"Third_Ward,_Houston",
 "Valinda Bolton":http://www.texastribune.org/directory/valinda-bolton/#ui-tabs-1" or "http://ballotpedia.org/Valinda_Bolton"
 }   
'''
#make these full links
#Ron Wilson ( has no wiki page .. so how to handle.. label as "none" and give desc or alternative url to use ?

#Why does WIKI desc for Talmadge Heflin not show up correctly no page (it just gives link to wiki page which redirects to correct spot..)
#SEE IF YOU CAN FIX THIS ONE.. can wiki follow redirect correctly??


# In[278]:

#des = get_wiki_des('TSU')                 #still gives Wikipedia disambiguation page
#des = get_wiki_link('Ron Wilson')
#des = get_wiki_link("Talmadge Heflin")   #gives 'http://en.wikipedia.org/wiki/Talmadge_L._Heflin'
                                          #THIS (using search php) WILL SOLVE ONLINE ISSUE SO IMPLEMENT AT HOME!
#des  #Wikipedia disambiguation page  ... for TSU

#save updated nodes with wikistubs
#with open('/Users/dolano/htdocs/dama-larca/d3/smallnet-revised-march26.json', 'wb') as fp:
#    json.dump(datasmr, fp)


# In[263]:

from bs4 import BeautifulSoup

def get_ballot_link(person):
    ret = ""
    try:
        URL = "http://ballotpedia.org/%s"        
        person = person.replace(" ","_")
        data = requests.get(URL % person )   
        if data.status_code == 200:
            link = data.url
            soup = BeautifulSoup(data.content)
            so = soup.find("div",{"id":"mw-content-text"})
            s = 0
            exit = 0
            output = ""
            for sc in so.children:
                if s >= 3 and exit == 0:  
                    if "<h2>" in str(sc):
                        exit = 1
                        break
                    else:               
                        output = output + str(sc)
                s = s + 1

            bsoup = BeautifulSoup(output)
            return [link,bsoup.get_text()]
        else:
            return ["",""]
        #TODO still gives Wikipedia disambiguation page for TSU, but fixes many of the 435!  look into this
    except:
        print("no link!")
        return ["",""]

#person = "Diego Olano"
#pp = get_ballot_link(person)
#print pp


# In[256]:

#soup.find("head")
#data.url  #http://ballotpedia.org/Valinda_Bolton


# In[259]:




# In[68]:

#global_index["Garnet Coleman"]
#global_entities[315]
goid = global_index["Garnet Coleman"]
x = entity_edges[goid]['edges']
xf = [ [v[v.keys()[0]],v.keys()[0]] for v in x]
most_assocatied_with_garnet_coleman = sorted(xf, reverse=True)

filtered_most_associated = []
exclude = ["Democrats","Democratic","Democrat","Houston Democrat","Houston Democrats","House Democratic","Houston-area","Houston Democratic","Democratic Representatives",
           "Republican","Republicans","Republican House","GOP","Republican Party","Justice","US","Texans","Houstonians","House Republicans",
           "House","two House","House floor","Senate","Congress","Texas Legislature","Legislature","Chronicle","State Senate","House Aug","Legislative",
           "House of Representatives","House Majority","Houston Chronicle","The Chronicle","Democrat Garnet Coleman","Obama Clinton",
           "American","janet .","chris .","Internet","University","The House","P.O.","contrast Bell","Council","Colemans",
           "Democrats Craddick","Tier","chairmen Pitts","Texas-Mexico","African-American","African-Americans","Capital",
           "Walt","Congressman Ryan","ID","Montessori","Bills","Taser","Tasers"]

for k in most_assocatied_with_garnet_coleman:
    ee = global_entities[k[1]]    
    if ee["full_name"] not in exclude  and k[0] >= 3:
        print "ADD: "+ee["full_name"] + "("+ee["entity_type"]+", "+str(k[1])+") - "+str(k[0])+" times"
        filtered_most_associated.append(k)

print("BEFORE MERGING size: "+str(len(filtered_most_associated)))  #368 direct connections before doing merging (which will bring it to 360ish)
#xxxNOW GET RID OF CERTAIN RELATIONS AS WELL (from exclude)


perry_in_entity_edges()


# In[ ]:




# In[204]:

#Republican Vasquez, Democrat Tony Sanchez, Democratic Gerry Birnberg,  ("Buice", "Jon Buice")
#Republican John Culberson, 
#Remove: Scott Street, ??Jim Leitner Pat Lykos


import sys
import requests
from bs4 import BeautifulSoup
 
def get_wiki_link(person):
    ret = ""
    try:
        URL = "http://www.wikipedia.org/search-redirect.php?family=wikipedia&search=%s&language=en"        
        person = person.replace(" ","%20")
        data = requests.get(URL % person )        
        soup = BeautifulSoup(data.content)
        head = soup.find("head")    #get canonical
        lnk = head.find("link",{'rel':'canonical'})
        ret = lnk.attrs['href']
        #TODO still gives Wikipedia disambiguation page for TSU, but fixes many of the 435!  look into this
    except:
        print("no link!")
    return ret
    
def get_wiki_photo(person):
    ret = ""
    try:
        URL = "http://en.wikipedia.org/w/api.php?action=query&titles=%s&prop=pageimages&format=json&pithumbsize=200"
        person = person.replace(" ","%20")
        data = requests.get(URL % person ).json()
        images = data['query']['pages']
        ret = images[images.keys()[0]]["thumbnail"]["source"]
    except:
        print("no wiki photo found")
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
        #print("no wiki description found")
        nothin = 1
    return ret

def get_wiki_shortbio(person):
    ret = ""
    #http://projects.knightlab.com/projects/metrovote
    try:
        person = person.replace(" ","%20")
        URL = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro=&explaintext=&titles=%s"
        data = requests.get(URL % person ).json()
        d = data['query']['pages']
        wikilink = "http://en.wikipedia.org/wiki/"+person
        ret = [ d[d.keys()[0]]['extract'] , wikilink ]
    except:
        print("no wiki short bio")
    return ret


# In[113]:

#"politician" in "American businessman and politician"
bio, link = get_wiki_shortbio("Garnet Coleman")


# In[116]:

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
        print "ERROR"
        
#def rename_ent(originalname,newname):
#    try:
#        gid = global_index[originalname]
        


# In[117]:

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


#Treina Wilson

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

                
    #!!Leland Anthony Hall  is actually Mickey Leland, Anthony Hall!  <-- ENDED ON HIM ( since after him its people with 4 mentions or less and i got tired)
#WHO IS Arthus Smith, Trish Wise??, #Terral Smith, 
#http://www.texastribune.org/directory/herschel-smith/
#global_entities[global_index["Priscilla Slade"]]["position"] = ["Former President Of Texas Southern University"]
#global_entities[global_index["John B. Coleman"]]  <-- father of Garnet Coleman
#Harsh Kumar  <-  wow
#TODO: MAKE FUNCTION SAY SOMETHING IF THERE IS DISAMBIGUATION TO BE FOLLOWED in WIKI calls
#TODO: for politician decision check for words, Senator, Represenative, President, legislator ( in addition to politician)
#if no wiki result, maybe add Texas to wiki query?


# In[128]:

#perry_in_entity_edges()   #still good here
#update_politician("Annise Parker","http://media.bizj.us/view/img/599811/annise-parker*400xx200-200-0-13.jpg"," Houston's second female mayor (after Kathy Whitmire), and one of the first openly gay mayors of a major U.S. city, with Houston being the most populous U.S. city to elect an openly gay mayor.")
#update_politician("Democratic Mario Gallegos","http://blogs.houstonpress.com/common/assets/475234.200s.jpg","was a Democratic politician in the U.S. state of Texas. He was the senator from District 6 in the Texas Senate, which serves a portion of Harris County","Mario Gallegos")
#update_politician("Terral Smith","http://static.politifact.com.s3.amazonaws.com/politifact%2Fmugs%2Fterralsmith2008square.jpg","former Republican Rep and legislative director for Gov. George W. Bush")
#update_politician("Ana Hernandez-Luna","","member of the Texas House of Representatives, representing the 143rd District.")


# In[129]:

for k in filtered_most_associated:
    ee = global_entities[k[1]]    
    if ee["full_name"] not in exclude  and k[0] >= 3:
        print "ADD: "+ee["full_name"] + "("+ee["entity_type"]+", "+str(k[1])+") - "+str(k[0])+" times"
    if k[1] == 496:
        print "^^^^^^^^^^^^^^^^RICK PERRY FOUND^^^^^^"


# In[130]:

#backup_of_filtered = filtered_most_associated[:]   this only does shallow copy .. FUCK!

from copy import deepcopy    #!!!!!
backup_of_filtered = deepcopy(filtered_most_associated)   

#len(backup_of_filtered)  368
for i,e in enumerate(backup_of_filtered):
    if i == 0:
        e[0] = 236
        break

for i,e in enumerate(backup_of_filtered):
    if i == 0:
        print e
        
for i,e in enumerate(filtered_most_associated):
    if i == 0:
        print e


#HMMM, it changed


# In[131]:

#735, 738, 741 ALL TAKE LONG STILL (why?)
#print len(entity_edges)   #2152
#print entity_edges[13]['counter'] #7416
#entity_edges[13]['edges']  #hmmm


#FOR NOW JUST DO MERGING LOCALLY AND keep track of equivalent ent_ids somehow
         #change id[0] for id[1]  so make sure id[0] has less hits then id[1] and then remove id[1] from list
merge = [("Texas Southern University","TSU"),("Governor Perry","Rick Perry"),("Medicaid-related","Medicaid"),
         ("University of Houston","UH"),("University of Texas","UT"),("young Medical Center","Medical Center"),
         ("DENVER Barack Obama","Barack Obama"),("Bush","George W. Bush"),
         ("Democrat Bill White","Bill White"),("R-Pampa Craddick","Tom Craddick"),("Craddick Craddick","Tom Craddick"),
         ("Craddick Ds","Tom Craddick"),("Tom Craddick House","Tom Craddick"),("Shelia Jackson Lee , state Representatives","Shelia Jackson Lee"),
         ("Democrat Borris Miles","Borris Miles"),("Houston Independent School District","HISD"),
         ("Delaware Hillary Clinton","Hillary Rodham Clinton"),("Health and Human Services","Texas Health and Human Services Commission"),
         ("Health and Human Services Commission","Texas Health and Human Services Commission"),("Texas Health and Human Services","Texas Health and Human Services Commission"), 
         ("Buice","Jon Buice"),("Fourth Ward Management District","Fourth Ward"),
         ("Children 's Health Insurance Program","CHIP"),("Democrat Tony Sanchez","Tony Sanchez"),
          ("Texas Department of Transportation","TxDOT"),("Democratic Gerry Birnberg","Gerald Birnberg"),
         ("HHSC","Texas Health and Human Services Commission"),("Democrat Sylvester Turner","Sylvester Turner") ]

#("Democratic Mario Gallegos","Mario Gallegos Jr"),
merge_ids = {}
for m in merge:
    #merge_ids.append[(global_index[m[0]],global_index[m[1]])]
    if global_index[m[1]] in merge_ids:
        merge_ids[global_index[m[1]]].append(global_index[m[0]])
    else:
        merge_ids[global_index[m[1]]] = [global_index[m[0]]]
 

 
merge_ids_flat = []
for yv in merge_ids.values():
    for yy in yv:
        merge_ids_flat.append(yy)

#print merge_ids_flat

merge_cnts = {}
for k in filtered_most_associated:
    if k[1] in merge_ids_flat:
        merge_cnts[k[1]] = k[0]
    
#print merge_ids    
    
prealias = deepcopy(filtered_most_associated)

#INCLUDE ALIAS SECTION
for i,k in enumerate(filtered_most_associated):
    ee = global_entities[k[1]]
    if k[1] in merge_ids_flat: 
        if k[1] == 496:
            print "&&&RICK PERRY"
            
        print("\tat i: "+str(i)+" GET RID of id ("+str(k[1])+") "+ee["full_name"]+" ... this record has been merged")
        
        del filtered_most_associated[i]  #MAYBE DON'T DO THIS CAUSE RICK PERRY LINKS ARE GOING MISSING
    else:        
        print ee["full_name"] + "("+ee["entity_type"]+", "+str(k[1])+") - "+str(k[0])+" times"
        alias_list = []
        if k[1] in merge_ids:                        
            mids = merge_ids[k[1]]
            for mid in mids:
                alias_list.append(mid)
                ee = global_entities[mid]
                print "\t included merged: "+ee["full_name"] + "("+ee["entity_type"]+", "+str(mid)+")"+str(merge_cnts[mid])+" times"
            k.append(alias_list)    
        else:
            k.append(alias_list)  #allias list empty

print("AFTER MERGING size: "+str(len(filtered_most_associated)))


# In[132]:

print 496 in [f[1] for f in filtered_most_associated]
perry_in_entity_edges()

for k in filtered_most_associated:
    ee = global_entities[k[1]]    
    if ee["full_name"] not in exclude  and k[0] >= 3:
        print "ADD: "+ee["full_name"] + "("+ee["entity_type"]+", "+str(k[1])+") - "+str(k[0])+" times"
    if k[1] == 496:
        print "^^^^^^^^^^^^^^^^RICK PERRY FOUND^^^^^^"


# In[133]:

near_entities_seen = []   #for nodes
for i,e in enumerate(filtered_most_associated):
    if e[1] not in near_entities_seen:
        near_entities_seen.append(e[1])

#print 1980 in near_entities_seen  #these are the near nodes
#print merge_ids    #496: [1980], 496 is true Rick Perry and 1980 is the one we want to set as an alias
#print "\n"
#print merge_ids_flat   #this includes 1980 and other ids we want to use as alias

alias_to_master = {}
for k in merge_ids:
    for v in merge_ids[k]:
        alias_to_master[v] = k
#print "\n"
#print alias_to_master   #now this is alias_id to masterid for quick look up

print len(near_entities_seen)


# In[134]:

#x = entity_edges[496]['edges']
#xf = [ [v[v.keys()[0]],v.keys()[0]] for v in x]
#most_assocatied = sorted(xf, reverse=True)
#most_assocatied_flat = [ m[1] for m in most_assocatied ]
#most_assocatied_flat
print 496 in [f[1] for f in filtered_most_associated]
perry_in_entity_edges()

for k in filtered_most_associated:
    ee = global_entities[k[1]]    
    if ee["full_name"] not in exclude  and k[0] >= 3:
        print "ADD: "+ee["full_name"] + "("+ee["entity_type"]+", "+str(k[1])+") - "+str(k[0])+" times"
    if k[1] == 496:
        print "^^^^^^^^^^^^^^^^RICK PERRY FOUND^^^^^^"


# In[137]:

#!!!!!!!!!!!!!!!!!!
#NOW TRY TO EXTEND NETWORK ONE OUT FOR EACH ENTITY IN filtered_most_associated, 
#THEN CREATE JSON FROM THAT and start viz!
#MAYBE ADD OLD LEGISLATORS and NEW SOURCE
#!!!!!!!!!!!!!!!!!!!

#Re-TAG incorrectly tagged entities (ex: Elgin is a Location, not an Organization)
#relabel Democrat Tony Sanchez to Tony Sanchez (Democrat), Democratic Gerry Birnberg, Republican John Culberson
#INCLUDE SOME MEASUREMENT OF HOW MANY DIFFERENT ARTICLES in ENTITY_EDGES

from copy import deepcopy
new_skip = ["civic",", Precinct", "Aggie", "Anthony Hall;", "BP", "Buice", "Coordinating Board", "Deeply-versed", 
            "Democrats Alma Allen", "Democrats alike", "Environmental Regulation", "Fair Houston", 'George " Mickey', 
            "Governor Perry", "Greater Southeast", "Hispanic Democratic", "Houston Democrats" , "Representatives", 
            "Houstonian", "LARA", "Latino", "Legislature Perry", "Lexicon", "Mickey Mouse", "Miss Thompson", 
            "National Alliance", "Perry Hispanic", "Place", "Politics", "Republican-dominated", "Ron Green;", 
            "Scott Street", "Shelia Jackson Lee , state Representatives", "Spanish", "Spanish", "Tom Craddick House", 
            "United", "Urban", "and Democratic Representatives", "majority-GOP Legislature", "nearby University", 
            "north of Memorial Drive", "with Precinct","To Coleman", "Tribune", "Texas Democrats", "Both Coleman", 
            "Texas Tribune Festival","RSVP",  "Jon Buice", 'Doc " Anderson', 'Mexican', 'Channel', 'Texas Politics',
            "Added Coleman", "Attorney", "Dallas Morning News", "Perry Hispanic", "Austin American-Statesman", 
            "Latino", "Texas Politics","Place","Republican Dominated","Laura Bush Opens","Dallas; Ray Allen","Jones",
            "Mando","Channel","Clinton Obama","Added Coleman","Both Coleman","To Coleman"]
            


    
    
#Then Build network from them
one_out_seen = []
one_out_nodes = deepcopy(near_entities_seen)  #you do this to pass a copy of near entities and not reference to it!
def make_network_one_out(fma,mc,debug=False):    
    #[ #links, #ent_id, #alias ids]    #links does not include those of aliases 
                                       #( they can be looked up via mc[mid] for now )
    final_net = {}
    gcoleman = global_index["Garnet Coleman"]
    final_net[gcoleman] = fma
    for i,e in enumerate(fma):
        
        try:
            times, eid, aliases = e
        except:
            if debug:
                printflush("Error in unpacking.  e is of size: "+str(len(e)))
                printflush(e)
                
            if len(e) == 2:
                if debug:
                    printflush("Size two so use as times, and eid")
                times, eid = e
                aliases = []
            else:
                if debug:
                    printflush("NOT SIZE 2 so skip")
                continue

        
        glob = global_entities[eid]
        if debug:
            printflush("&&&&& at "+str(i)+": CURRENTLY HANDLING: "+glob["full_name"] + "("+glob["entity_type"]+", "+str(eid)+") - with aliases: "+str(aliases))            
            #printflush("\t Connections to Coleman - str(times)+" times 
            
        x = entity_edges[eid]['edges']
        xf = [ [v[v.keys()[0]],v.keys()[0]] for v in x]
        most_assocatied = sorted(xf, reverse=True)
        most_assocatied_flat = [ m[1] for m in most_assocatied ]
        filt_most_assoc = []
        if debug:
            printflush("\tBEFORE FILTER/MERGING size: "+str(len(most_assocatied_flat)))
                       
        for k in most_assocatied:
            if k[1] == gcoleman or k[1] in aliases or k[1] in one_out_seen: 
                #if id is Garnet Colemans or one of our aliases or already has an edge with this k[1] from prior loops don't use
                #if debug:
                    #printflush("\tFound GC or alias so skip id: "+str(k[1])+" !")
                continue
                
            ee = global_entities[k[1]]            
            if ee["full_name"] not in exclude and ee["full_name"] not in new_skip  and k[0] >= 2:   #maybe make this 3 smaller so you can get nodes farther out?
                
                if debug: # and i < 2:
                    printflush("ADD: "+ee["full_name"] + "("+ee["entity_type"]+", "+str(k[1])+") - "+str(k[0])+" times")
                                                                 
                #NOW HANDLE ALIASES FOR K              
                if k[1] in merge_ids_flat:    
                    if debug:
                        printflush("\t XXX"+ee["full_name"]+" ... this record has been merged.. Check if it exists here and if not add it")
                    
                    if alias_to_master[k[1]] in most_assocatied_flat:                         
                        if debug:
                            printflush("----Yes it is so remove it")
                        #del filt_most_assoc[i] # just don't append it
                        continue 
                    else:
                        if debug:
                            printflush("----No it isn't so add it by constructing a new k")
                        k = [k[0],alias_to_master[k[1]],[k[1]]]
                else:                                           
                    alias_list = []
                    if k[1] in merge_ids:         #these are master ids               
                        mids = merge_ids[k[1]]
                        for mid in mids:
                            alias_list.append(mid)
                            ei = global_entities[mid]
                            if debug:
                                printflush("\t included merged: "+ei["full_name"] + "("+ei["entity_type"]+", "+str(mid)+")"+str(mc[mid])+" times")
                        k.append(alias_list)    
                    else:
                        k.append(alias_list)  #allias list empty
                
                filt_most_assoc.append(k)  
                
                if k[1] not in one_out_nodes:
                    one_out_nodes.append(k[1])  #at the end, one_out_node will be what we use to construct large nodes list, 
                                                #and final net will be used to make large edges list.
                        
                                                #whereas near_entities_seen will be used to construct small nodes list
                                                #and filtered_most_associated will be used to make small edges list.
            #else:
                #if debug and k[0] >= 2:
                #    printflush("Skipped "+ee["full_name"])
                
        if debug:
            printflush("\tAFTER FILTER/MERGING FOR EID("+str(eid)+") size: "+str(len(filt_most_assoc))) 
        final_net[eid] = filt_most_assoc  
        one_out_seen.append(eid)
    
    return final_net


prelong = deepcopy(filtered_most_associated)  #use this maybe to generate short json
final_net = make_network_one_out(filtered_most_associated,merge_cnts,False)





#Houston Bills?    
#ID
#Day Massacre
#HB (look for bill number)
#Children 's Defense Fund and John O 'Quinn  <-- TODO: FIX THIS ISSUE IN CODE
#House Majority <-- TODO: should be followed by something
#Capital and Metro were found independently hmm...
    #Why aren't BILLS SHOWING UP Higher?  maybe its just for Garnet (or they aren't close to him)


# In[138]:

print 496 in [f[1] for f in filtered_most_associated]
perry_in_entity_edges()

for k in filtered_most_associated:
    ee = global_entities[k[1]]    
    if ee["full_name"] not in exclude  and k[0] >= 3:
        print "ADD: "+ee["full_name"] + "("+ee["entity_type"]+", "+str(k[1])+") - "+str(k[0])+" times"
    if k[1] == 496:
        print "^^^^^^^^^^^^^^^^RICK PERRY FOUND^^^^^^"

print len(filtered_most_associated)  #352
print len(near_entities_seen)        #352


# In[145]:

tot = 0
for f in final_net:
    tot = tot + len(final_net[f])
    
print "##TOTAL NUMBER OF EDGES: "+str(tot)    #2145
print "#EDGES AROUND GARNET ALONE: "+str(len(final_net[315]))  #  352
#print final_net.keys()

#look to see 496 and 431  ( Perry and Craddick ) point to each other ( ie, double counting edges for non garnet)
rp = final_net[496]
rp_flat = [ r[1] for r in rp ]
print 431 in rp_flat   #Craddick in edges for Perry?

tc = final_net[431]
tc_flat = [ t[1] for t in tc ]
print 496 in tc_flat    #Perry in edges for Craddick?  THIS IS TO VERIFY WE DON'T DOUBLE COUNT EDGES WHEN WE GROUP ALL

#print len(near_entities_seen)
#print near_entities_seen
#print "\n"
#print len(one_out_nodes)
#print one_out_nodes

#print len(filtered_most_associated)

#json_output["elements"]["nodes"]

##TOTAL NUMBER OF EDGES: 15724
#EDGES AROUND GARNET ALONE: 662
#False
#False
print len(final_net.keys())
print global_index


# In[146]:

#at the end, one_out_nodes will be what we use to construct LARGE nodes list, 
#and final_net will be used to make large edges list.
from copy import deepcopy
def construct_large_json(one_out_nodes,final_net):
    #print len(one_out_nodes) #all nodes including from one away that we've seen, 798
    #print len(final_net) #353
    #print final_net.keys() #each key is a global_entity_id
    large_json_output = {"elements":{"nodes":[],"edges":[]}}
    possible_edges = deepcopy(json_output["elements"]["edges"])    #copy by value, not reference
    gcoleman_id = global_index["Garnet Coleman"]
    
    #populate nodes
    for i,gid in enumerate(one_out_nodes):
        gent = global_entities[gid]
        
        del gent["id"]
        if "_id" in gent:
            del gent["_id"]
            
        gent["id"] = gid
        if 'sentence' in gent:
            del gent['sentence']
            
        large_json_output["elements"]["nodes"].append({"data":gent})   #add nodes, make sure entity_type is here

    #populate edges   
    text_ids_needed_for_demo = []
    
    count = 0 #for debuging only
    for e,edg in enumerate(possible_edges):
                                       
        sid = edg["data"]["source"]
        tid = edg["data"]["target"]
        if sid not in one_out_nodes or tid not in one_out_nodes:            
            nothing = 1
        else:             
            large_json_output["elements"]["edges"].append(edg)
            count = count +1 
            for tee in edg["data"]["inst"]:
                if tee["textid"] not in text_ids_needed_for_demo:
                    text_ids_needed_for_demo.append(tee["textid"])
    
    #print "Count: "+str(count)
    return [large_json_output,text_ids_needed_for_demo ]
        
#whereas near_entities_seen will be used to construct SMALL nodes list
#and filtered_most_associated will be used to make small edges list.
def construct_small_json(near_entities_seen,filtered_most_associated):
    print "in small json"
    small_json_output = {"elements":{"nodes":[],"edges":[]}}
    possible_edges = deepcopy(json_output["elements"]["edges"])   #copy by value, not reference
    gcoleman_id = global_index["Garnet Coleman"]

    
    fa = deepcopy(filtered_most_associated)
    nes = deepcopy(near_entities_seen)
    nes.append(gcoleman_id)
    
    #populate nodes
    for i,gid in enumerate(nes):
        gent = global_entities[gid].copy()
        
        del gent["id"]
        if "_id" in gent:
            del gent["_id"]
            
        gent["id"] = gid

        if 'sentence' in gent:
            del gent['sentence']
            
        #if gid == 496:
        #    print "Add Rick Perry to nodes"
        #    print gent
            
        small_json_output["elements"]["nodes"].append({"data":gent})   #add nodes, make sure entity_type is here
          
    #populate edges
    fma_flat = [ f[1] for f in fa]
    text_ids_needed_for_demo = []
    
    #print len(possible_edges)
    #print "GColeman: "+str(gcoleman_id)
    #print filtered_most_associated_flat
    
    print 496 in fma_flat
    
    count = 0 #for debuging only
    for e, edg in enumerate(possible_edges):
                                       
        #only include Garnet Coleman as source and  
        sid = edg["data"]["source"]
        if sid != gcoleman_id:            
            #print str(e)+": Delete cause source ain't GC! "+str(sid)
            #del small_json_output["elements"]["edges"][e]
            nothing = 1
            tid = edg["data"]["target"]
            #if tid == 496:
            #    print "!!!!!!!!!SKIPPED RICK PERRY"
            #    print edg
        else:             
            #check that target is in filtered_most_associated_flats (ie, those with GC).  if not get rid of it
            tid = edg["data"]["target"]
            if tid == 496:
                print("Will Rick Perry make the cut?")
            if tid not in fma_flat: #filtered_most_associated_flat:                
                #print str(e)+": Delete cause target ain't in! "+str(tid)
                #del small_json_output["elements"]["edges"][e]
                nothing = 1
            else:
                #print str(e)+": Add edge with sid: ("+str(sid)+" and tid: "+str(tid)+")"
                if tid == 496:
                    print "!!!!!!!!!ADD RICK PERRY"
                    print edg
                    
                small_json_output["elements"]["edges"].append(edg)
                count = count +1 
                for tee in edg["data"]["inst"]:
                    if tee["textid"] not in text_ids_needed_for_demo:
                        text_ids_needed_for_demo.append(tee["textid"])
    
    #print "Count: "+str(count)
    return [small_json_output,text_ids_needed_for_demo ]

sm_jo, text_ids_needed_for_demo  = construct_small_json(near_entities_seen,filtered_most_associated)
print "Nodes: "+str(len(sm_jo['elements']['nodes']))  #357
print "Edges: "+str(len(sm_jo['elements']['edges']))  #352 
print "Text Snippets: "+str(len(text_ids_needed_for_demo)) #3688


# In[147]:

print 496 in [f[1] for f in filtered_most_associated]
perry_in_entity_edges()

for k in filtered_most_associated:
    ee = global_entities[k[1]]    
    if ee["full_name"] not in exclude  and k[0] >= 3:
        print "ADD: "+ee["full_name"] + "("+ee["entity_type"]+", "+str(k[1])+") - "+str(k[0])+" times"
    if k[1] == 496:
        print "^^^^^^^^^^^^^^^^RICK PERRY FOUND^^^^^^"


# In[148]:

#496 in filtered_most_associated_flat

#Nodes: 353
#Edges: 346
#Text Snippets: 3200

#for i,e in enumerate(sm_jo['elements']['edges']):
#    if i < 3:
#        print "\n%%%%%%%%%%"+str(i)+": "+str(e)
        

#for i,e in enumerate(sm_jo['elements']['nodes']):
#    if i < 3:
#        print "\n%%%%%%%%%%"+str(i)+": "+str(e)

#496 in [f[1] for f in filtered_most_associated]  #TRUE
#496 in [ f['data']['id'] for f in sm_jo['elements']['nodes']] #TRUE
ns = [ f['data']['id'] for f in sm_jo['elements']['nodes']]
print len(ns)   #353


# In[149]:

#HANDLE SMALL CASE
#-----------------------------------------------------------------------------------------

#nodes_sorted_by_id = sorted(sm_jo['elements']['nodes'], key=lambda k: k['data']['id']) 
#for i,e in enumerate(nodes_sorted_by_id):
#    if i < 13:
#        print str(i)+": "+ str(e['data']['id'])+' , '+e['data']['full_name']

#D3 wants the source and target values to match the numbered index of the nodes
#so we need to make a map of our node entity id's to their index ids, 
#print nodes_sorted_by_id  .. nodes found in nodes


#print sm_jo['elements']['edges']

#1.  only include nodes which are definitely linked to!!  
all_link_nodes = []
for i, e in enumerate(sm_jo['elements']['edges']):
    #print e
    if e['data']['source'] not in all_link_nodes:
        print("ADD source: "+str(e['data']['source']))
        all_link_nodes.append(e['data']['source'])
        
    if e['data']['target'] not in all_link_nodes:
        print("ADD target: "+str(e['data']['target']))
        all_link_nodes.append(e['data']['target'])

print len(all_link_nodes)  #353 if this is working correctly!


# In[150]:

#2.  remove nodes not in all_link_nodes
newnodes = []
for i,n in enumerate(sm_jo['elements']['nodes']):
    #print n
    if n['data']['id'] in all_link_nodes:
        newnodes.append(n)
    else:
        print(str(i)+": didn't find the following in all_link_nodes: "+str(n['data']['id']))


print "nnodes: ",len(newnodes)  #there should be no "didn't find messages!"


# In[151]:

#3.  make dict from entid to nodes index id
entid_to_node = {}
index_to_endit = {}
for i,n in enumerate(newnodes):
    entid_to_node[n['data']['id']] = i
    index_to_endit[i] = n['data']['id']


# In[152]:

print index_to_endit[entid_to_node[496]]


# In[153]:

#4.  and then change all links to use them!
newlinks = deepcopy(sm_jo['elements']['edges'])
for i,e in enumerate(newlinks):
    e['data']['source'] = entid_to_node[e['data']['source']]
    e['data']['target'] = entid_to_node[e['data']['target']]


# In[154]:

newlinks[0]


# In[365]:

#check Perry
print 496 in [f[1] for f in filtered_most_associated]
perry_in_entity_edges()

for k in filtered_most_associated:
    ee = global_entities[k[1]]    
    if ee["full_name"] not in exclude  and k[0] >= 3:
        print "ADD: "+ee["full_name"] + "("+ee["entity_type"]+", "+str(k[1])+") - "+str(k[0])+" times"
    if k[1] == 496:
        print "^^^^^^^^^^^^^^^^RICK PERRY FOUND^^^^^^"

rid = entid_to_node[496] #Rick Perry Index
print "Rick Perry Index: "+str(rid)
for i,e in enumerate(newnodes):
    if i == rid:
        print "Is this Rick Perry at index: "+str(i)
        print e


c = 0
for el in newlinks:
    if el['data']['source'] == 0 or el['data']['target'] == 0:
        c = c+1
        print el
print "Total for Perry: "+str(c)


# In[155]:

#5.  change sm to use new nodes and new links
sm_jo["elements"]["nodes"] = newnodes
sm_jo["elements"]["edges"] = newlinks


# In[159]:

#check url_list for urls json if needed
url_list  #if this is undefined, run generate_url_list function below!


# In[160]:

#newnodes[352]  #Garnet Coleman
#newnodes[0] #Rick Perry
for i,n in enumerate(newnodes):
    print str(i)+": "+n["data"]["full_name"]+"("+str(n["data"]['id'])+")"

#1) save REVISED small json file  (TODO:  maybe get rid of mongoid stuff)
#with open('/Users/dolano/htdocs/dama-larca/d3/smallnet-revised-march17.json', 'wb') as fp:
#    json.dump(sm_jo, fp)

#2) save small text snippets file
#print(text_ids_needed_for_demo)  list of ids
textjson = {}
for t in text_ids_needed_for_demo:
    textjson[t] = text_snippets[t]

#with open('/Users/dolano/htdocs/dama-larca/d3/smallnet-textsnippets-march17.json', 'wb') as fp:
#    json.dump(textjson, fp)

#3) write mongo - url dict
with open('/Users/dolano/htdocs/dama-larca/d3/smallnet-urls-march17.json', 'wb') as fp:
    json.dump(url_list, fp)


# In[ ]:

#now check on three JSON FILES CREATED AND SEE IF THEY WORK


# In[223]:

lg_jo, lg_texts_needed = construct_large_json(one_out_nodes,final_net)
print "Nodes: "+str(len(lg_jo['elements']['nodes']))  #798
print "Edges: "+str(len(lg_jo['elements']['edges']))  #5573 
print "Text Snippets: "+str(len(lg_texts_needed)) #9128


# In[378]:

print "Nodes: "+str(len(lg_jo['elements']['nodes']))  #798
print "Edges: "+str(len(lg_jo['elements']['edges']))  #5573 
print "Text Snippets: "+str(len(lg_texts_needed)) #9128


# In[410]:

#TODO: make sure LARGE is correct (only use nodes seen in links, change links to use ids of order of nodes, etc)
#print lg_jo['elements']['nodes'][0] 
#print sm_jo['elements']['nodes'][0]
 
sylvid = global_index['Sylvester Turner']   #337
borrid = global_index['Borris Miles'] #148
rodnid = global_index['Rodney Ellis'] #458
cradid = global_index['Tom Craddick'] #431        
perrid = global_index['Rick Perry'] #496
medcid = global_index['Medicaid'] #633
tsuid =global_index['TSU'] #601

topents = [sylvid, borrid, rodnid, cradid, perrid, medcid, tsuid]
links_between_top_50 = [{t:{}} for t in topents]
for i,l in enumerate(links_between_top_50):
    curl = l.keys()[0]
    ll = l[curl]
    ente = entity_edges[curl]
    for t in ente['edges']:
        turl = t.keys()[0]
        if turl != curl and turl in topents:
            ll[turl] = t[turl] 

#[{337: {458: 7, 431: 33, 496: 2, 148: 2, 633: 2, 601: 4}}, 
# {148: {496: 9, 337: 2, 458: 2, 431: 3}}, 
# {458: {496: 19, 601: 19, 148: 2, 633: 11, 337: 7}}, 
# {431: {496: 6, 337: 33, 148: 3, 633: 2}}, 
# {496: {458: 19, 431: 6, 337: 2, 148: 9, 633: 17, 601: 24}}, 
# {633: {496: 17, 337: 2, 458: 11, 431: 2}}, 
# {601: {496: 24, 337: 4, 458: 19}}]            
            
for lb in links_between_top_50:
    lk = lb.keys()[0]
    #print global_entities[lk]['full_name']+": "
    #for cc in lb[lk]:
    #    print "\t"+str(lb[lk][cc])+" - "+global_entities[cc]['full_name']
    #print("")


# In[414]:

#len(url_list)   #mongo list
#url_list
len(text_snippets)  #size 50693.. so add 


# In[394]:

entity_edges[337]


# In[227]:

#HANDLE LARGE CASE
#-----------------------------------------------------------------------------------------
#for i,e in enumerate(lg_jo['elements']['edges']):
#    if i < 3:
#        print "\n%%%%%%%%%%"+str(i)+": "+str(e)


#for i,e in enumerate(lg_jo['elements']['nodes']):
#    if i < 3:
#        print "\n%%%%%%%%%%"+str(i)+": "+str(e)


#1) save large json file  (TODO:  maybe get rid of mongoid stuff)
#with open('/Users/dolano/htdocs/dama-larca/d3/largenet.json', 'wb') as fp:
#    json.dump(lg_jo, fp)

#2) save small text snippets file
#print(lg_texts_needed)  list of ids
#largetextjson = {}
#for t in lg_texts_needed:
#    largetextjson[t] = text_snippets[t]

#with open('/Users/dolano/htdocs/dama-larca/d3/largenet-textsnippets.json', 'wb') as fp:
#    json.dump(largetextjson, fp)

#3) use same mongo - url dict


# In[ ]:

#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################
#FROM HERE ON ITS JUST SCRATCH PAD STUFF FOR NOW UNTIL REFACTORING ######################################
#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################


# In[171]:

#NEW TODO, why is 735 so slow (ones at end get slow)

#these indexes go slow 27,48, 581, 738 
#print "." * 10
import operator
x = article_entity_lens
sorted_x = sorted(x.items(), key=operator.itemgetter(1),reverse=True)
print sorted_x[0:30]    #wow!

slow  = [27,  48,71,581,735,738,741,752,759,767,770]
found = [297,125,88,106,146,140, 94,84 ,113,307,85 ]
#for s in slow:
#    id =  x[s][1]
#    print("A: "+str(s)+", ID: "+str(id)+", URL: "+x[s][2])
    #get_article_from_mongo_by_id(id,db):
#TODO MAKE SURE YOU ARENT GETTING FALSE POSITIVES

#FOR SLOW ONES (ie, any which have how many initial entities create?) , ONLY ADD EXTRA's FOR SAME and NEARs (No fars)


# In[1302]:



xxx#1. TODO add interarticle links that aren't the primary politican centric (eventually do full)  NOW DO THIS!
xxx #2. TODO: ADD ABILITY TO HANDLE MULTIPLE DIRECT HITS ( MOST IMPORTANT)  see a = 4
#  ( SEE GET_RELATIONS, JUST NEED TO BE CLEVER ABOUT MERGING EITHER IN THAT FUNCTION
#    OR IN VERIFY WHEN ADDING RELATIONS, NEED TO INCLUDE ENT_ID TO DIFFERENTIATE or for second only worry about direct hits maybe? )

#2.4 Use alliases [Democrats, Democratic Party, Democrat, ]
xxx #2.5 Don't allow single names to be added as PERSON's , see a=11    !!!  or as MISC's
        #janet .(295) -- kristen(298)   terrible
xxx #2.6 TODO: disambiguate_ printflush("????FOUND possible names that should be combined: "+prior['text']+" and "+t)
     #combine the prior PERSON and this person into ONE, if this person is of size one
xxx #2.7 handle "House Speaker"    
    
#3. Get One or two more sources (texas tribune, dallas morning news)
#4. TODO ADD KEYWORDS/FREQUENCY STUFF (IMPORTANT) - incorporate Francisco's stuff
#5. TODO ADD MANNER IN WHICH TO GET FEDERAL TEXAS REPS INFO SENATORS/REPS, ALONG WITH OTHER IMPORTANT OFFICES! 
#   (VERY IMPORTANT)

#TODO: populate with all politicians you can from before ( Federal and State Level) .. specifically prior texas wide legislatures!!
#TODO: MAYBE LOOK INTO TITLES AFTER WORD (where as now we only do prior)
#TODO USING WIKIPEDIA TO FIND ALIASES/VERIFY ENTITIES ( http://live.dbpedia.org/page/George_W._Bush )
#TODO AFTER INITIAL SEARCH, LOOK FOR ANY UPPERCASE WORDS NOT INCLUDED IN THE MIX AND DECIDE WHAT THEY ARE. (IMPORTANT-ish)
#TODO DON'T ALLOW PERSONS WITH ONE NAME TO GET ADDED TO GLOBAL LIST ( see, janet.)
#TODO WEIGH IMPORTANCE OF REFERENCES IN A GIVEN ARTICLE BY TOTAL NUMBER OF REFERENCES OVERALL (see a=27, candidate list!!)
#TODO: MAKE SIMPLE TOOL TO JOIN ENTITIES FROM GLOBAL RELATIONS DB WHICH ARE ACTUALLY THE SAME ( that propogates)

#TODO: pre-assess if any pairs of words are in all caps, and then make them just normal capitalized 
#     ( case a = 128, SEN. JUAN "CHUY" HINOJOSA, D-McALLEN ... finds D-McALLEN as person).. maybe just change this thing
#TODO: check if an article doesn't have same info as its webpage!!
#TODO: add district name/city to politicians at beginning for help in verifying things, and county
#TODO: add committees, http://sunlightlabs.github.io/openstates-api/committees.html#committee-fields
#TODO: add finance contributions stuff
#TODO cases:
    #Houston Democrat Representative Garnet Coleman ( gets rep, but not democrat or houston) <--
    #ORG NOT FOUND:   Pro-Choice Texas Foundation-NARAL
    #Representative Inocente "Chente" Quintanilla , treated as MISC: Inocente , MISC: Chente, PERSON: Quintanilla
    #Harris County Attorney 's Office <-- watch for extra space
    #for a=16, Lieutenant Governor Bill Ratliff and House Speaker Pete Laney ( make sure this works)
    #fixed error at 189, AAAAAA: Looking if word after to LOCATION AUSTIN U.S. is in CAPS and part of an ORGANIZATION NAME
        #[u'AUSTIN', u'\u2014', u'U.S.']
        #check is U.S.
        #if ps[i+1].replace(":","").replace(",","") != t.split()[1]:
        #list index out of range
    # error at ****155***id: 645659, 2012-10-14
        #http://www.chron.com/news/houston-texas/article/Cancer-agency-faces-challenges-in-months-ahead-3945706.php
        #ZZZZZZZZZZ No hit found in article    
        #State Rep. Garnet  Coleman   (DOUBLE SPACE SCREWED US so remove from doc and try again)
    # error at ****480***id: 6568312013-02-22
        #http://www.chron.com/opinion/editorials/article/Is-there-really-a-Houston-delegation-in-the-Texas-4301557.php
        #ZZZZZZZZZZ No hit found in article
        #6. Garnet  Coleman, D .. same exact DOUBLE SPACE ISSUE!
    

#XXX: get districts json
   #http://openstates.org/api/v1/districts/tx/?apikey=744e7bf0a08748e69f06d690d8aa197c
#XXX: get counties json
   #http://jasonweaver.name/lab/texascounties/



#FOR HOUSTON CHRONICLE, if link says Legislature-highlights, don't include "same article" catches

#for Garnet Coleman
#for 771 results, we process it in 32.717454 seconds
#GLOBAL INDEX with 7172 entities
#GLOBAL RELATIONS with 767 articles and 
#Total Relations of 22913

#using multiple match now, it takes 34 seconds 
#GLOBAL INDEX 7172 entities
#GLOBAL RELATIONS 767 articles
#Total Relations 24530

#with both multiple match and interarticle links and not adding far-far extras if more than 80 entities found, 
#    it takes 89.66 seconds
#GLOBAL INDEX 6905 entities
#GLOBAL RELATIONS 767 articles
#Total Relations 271940

#consolidating things and not including "same article relations we get", though it takes 540 seconds
#GLOBAL INDEX 6905 entities , 
#GLOBAL RELATIONS 767 articles
#Total Relations 271940
#Number of Json Edges:58818

#consolidating things and not including "same article relations" or "LOCATION" relations it takes 435.68
#GLOBAL INDEX 6905 entities
#GLOBAL RELATIONS 767 articles
#Total Relations 271940
#Number of Json Edges:42379

#consolidating things, not including 'same article',"LOCATION", or far far extras at all, takes 146.55975 seconds
#GLOBAL INDEX 6905 entities
#GLOBAL RELATIONS 767 articles
#Total Relations 69515
#Number of Json Edges:26438


# In[198]:

#print "GLOBAL ENTITIES"
#for ge in global_entities:
#    print ge['full_name']
print "\nGLOBAL INDEX "+str(len(global_index)) + " entities"
print "\nGLOBAL RELATIONS "+str(len(global_relations)) + " articles"
total = 0
for gr in global_relations:    
    if total < 0:
        for g in global_relations[gr]:
            if g not in ["relations","entities"]:
                print g+": "+str(global_relations[gr][g])
            else:
                print g+": "+str(len(global_relations[gr][g]))
                
        print "\nEntities"
        #print global_relations[gr]["entities"]
        print "\nRelations"
        #for r in global_relations[gr]["relations"]:
        #    print r
        
    total = total + len(global_relations[gr]['relations'])

print "\nTotal Relations "+ str(total)
print "\nGlobal Entities (should match size of global index) "+ str(len(global_entities))

print "\nNumber of Json Edges:" + str(len(json_output["elements"]["edges"]))

#print global_entities[190]
#print global_index[global_entities[190]["full_name"]]


# In[199]:

#save prior for use
ge_prior = []
gr_prior = {}
gi_prior = {}

def make_backup():
    gr_prior = global_relations.copy()
    ge_prior = global_entities.copy()
    gi_prior = global_index.copy()
    
def retreive_from_backup():
    global_relations = gr_prior.copy()
    global_entities = ge_prior.copy()
    global_index = gi_prior.copy()


def print_global_index_and_entities():
    for i,gi in enumerate(global_index):
        #manual adds start at 181
        if global_index[gi] >= 180:
            print str(global_index[gi])+" : "+gi + ", " + str(global_entities[global_index[gi]])

def print_global_relations():
    for i,gr in enumerate(global_relations):
        print str(i)+" : "+gr

        for e,g in enumerate(global_relations[gr]['relations']):
            print e,g['term1_id'],g['term2_id'],g['term1'],g['term2']
    
        #print global_relations[gr]


#str(len(global_relations))
#if str(len(global_relations))
for i,gr in enumerate(json_output["elements"]["edges"]):
    if i == 0:
        print gr
        break

def global_relations_to_entity_centric():    
    # is this necessary    
    entity_centric = global_entities
    #for gr in global_relations:
      
        
url_list = {}
def generate_url_list():
    #make url list indexed by mongoid so that edges just need mongoid to show id
    #TODO: in future this will be in mongodb
    for i,gr in enumerate(global_relations):
        mongoid = global_relations[gr]['mongoid']
        url_list[mongoid] = {'url':global_relations[gr]['url'], 'date': global_relations[gr]['date'],
                             'num_sentences':global_relations[gr]['num_sentences'], 
                             'entities':len(global_relations[gr]['entities']),
                             'relations':len(global_relations[gr]['relations'])}
    
generate_url_list()

def generate_json():
    #THIS JUST ADD NODES NOW
    #populate nodes
    for i,ge in enumerate(global_index):
        fname = ge   #full name
        gid =  global_index[ge]  #gid
        gent = global_entities[gid]
        
        del gent["id"]
        gent["id"] = gid
        if 'sentence' in gent:
            del gent['sentence']
            
        #if gid > 180:
        json_output["elements"]["nodes"].append({"data":gent})

    #populate edges
    '''
    edges_seen = []

    
    #test on subset now
    
    global_rels = global_relations_sub      #global_relations

    for i,gr in enumerate(global_rels):
        print str(i)+" : "+gr
        #u'num_sentences': 3, u'date': u'2001-03-14'
                       
        for r in global_rels[gr]['relations']:
            #print r
            inst = {}
            inst['source'] = r['term1_id']
            inst['target'] = r['term2_id']
            
            #z = r.copy()  #this is necessary so you don't change value of global r
            #z.update(e)   #to merget e, but we no longer need it           
            ei = {}
            ei['type'] = r['type']
            ei['mongoid'] = global_rels[gr]['mongoid']
            if ei['type'] != 'same article':
                textid = add_text_snippet(r['text_snippet'])
                ei['textid'] = textid
            else:
                continue #for now don't include relations which are just same article
            
            inst['inst'] = [ei]
            
            #check if it exits, either source-target or target-source
            if [inst['source'],inst['target']] in edges_seen or [inst['target'],inst['source']] in edges_seen:
                s,t = [inst['source'],inst['target']] if [inst['source'],inst['target']] in edges_seen else [inst['target'],inst['source']]

                #get existing edge and just add r to ['inst'] of it
                for edg in json_output["elements"]["edges"]:
                    if edg['data']['source'] == s and edg['data']['target'] == t:
                        edg['data']['inst'].append(ei)
                        break
                
            else:
                edges_seen.append([inst['source'],inst['target']])
                json_output["elements"]["edges"].append({"data":inst})
    '''


# In[133]:

#print url_list.keys()
#print url_list["235595"]


# In[202]:


#function which allows you to rename a global entity, this function is fast enough 
def rename_global_entity(gid,text,debug=False):    
    ret = False
    try:
        prior_text = global_entities[gid]['full_name']
    except:
        prior_text = ""

    if debug:
        print "Prior text: "+prior_text
    
    if prior_text == "":
        if debug:
            print "Error: No prior text found so can't update it"
    else:
        #make sure "text" not already a pre-existing entity cause then you'll need to merge
        if text in global_index:
            if debug:
                print "Error value of "+text+" already exists in global_index so we can't add it.  Possible merge?"
                print global_entities[global_index[text]]
        else:
            #rename old global_index so it reflects new text
            if debug:
                print "Remove: "+prior_text+" from global_index and add: "+text
                
            global_index[text] = global_index[prior_text]
            del global_index[prior_text]

            #finally change name of global entity
            if debug:
                print "Add text "+text+" to global_entities at gid: "+str(gid)
            global_entities[gid]['full_name'] = text     
            ret = True
    return ret


#THIS IS BASED ON OLD GLOBAL_RELATIONS AS OPPOSED TO json_output
#function to delete an entity which is bullshit, 
#          delete from global index, but also delete any relations which have that gid as a source or target!
#need to re-run generate_json to update things global json we save
def delete_global_entity(gid,text,debug=False):
    #make them pass both text and gid as verification
    success = False
    if debug:
        printflush("In Delete Entity with gid:"+str(gid)+" and text:" + text)
    try:
        if global_entities[gid]['full_name'] != text:
            printflush("Entity corresponding to gid: "+str(gid)+" "+global_entities[gid]['full_name']+" not equal to "+text+" so abort") 
        else:
            #delete from global_index, global_entities and delete from relations
            del global_index[text]
            del global_entities[gid]
            num_deleted = 0
            for i,gr in enumerate(global_relations):
                for e,g in enumerate(global_relations[gr]['relations']):
                    #e,g['term1_id'],g['term2_id'],g['term1'],g['term2']
                    if g['term1_id'] == gid or g['term2_id'] == gid:
                        if debug:
                            printflush("Found gid: "+str(gid)+" so delete the following which includes it")
                            printflush(g)
                        del global_relations[gr]['relations'][e] 
                        num_deleted = num_deleted + 1
            if debug:
                printflush("Delete successfull.  Deleted "+str(num_deleted)+" relations")
            success = True
    except:
        if debug:
            printflush("Error in looking for "+str(gid)+" in global_entities.  Delete "+text+" aborted")
    
    return success


#THIS IS BASED ON OLD GLOBAL_RELATIONS AS OPPOSED TO json_output
#function to merge two entities which are the same, and give them a common name (which can be equal to either or new)
#          keep id of one of the two, rename that id to common name, 
#          and change all relations which have deleted id to the one kept between the two
def merge_global_entities(gid,gid2,name,debug=False):
    
    #TODO: change this so that it renames id which appears less frequently cause this takes too long
    #    probably need to do merge on entity centric list (ie, json relations newlist )
    #TODO: add timer stuff here ( cause it takes for god damn ever ) and keep track of relations you merged
    #TODO: add which ever name you remove to the alias array for the object !!   VERY IMPORTANT
        
    #first figure out which entity to keep
    success = False
    ret_id = -1
    
    if debug:
        printflush("In Merge global entitites: "+str(gid)+" and "+str(gid2)+" and keep/change to name "+name)
    try:
        #first change entity id for one you aren't keeping to the one you are keeping in relations
        #then delete global_index and global_entities objects refering to old one        
        #then change name if necessary
        
        if global_entities[gid2]['full_name'] == name:            
            #Here we are keeping gid2, so change entity gid to gid2 in relations
            num_changed = 0
            for i,gr in enumerate(global_relations):
                for e,g in enumerate(global_relations[gr]['relations']):                    
                    if g['term1_id'] == gid or g['term2_id'] == gid:
                        if debug:
                            #printflush("Found gid: "+str(gid)+" so change it to "+str(gid2))
                            #printflush(g)
                            printflush(".",False)
                            
                        if g['term1_id'] == gid:
                            global_relations[gr]['relations'][e]['term1_id'] = gid2
                        else:
                            global_relations[gr]['relations'][e]['term2_id'] = gid2
                        num_changed = num_changed + 1
            if debug:
                printflush("Changed from old gid to new one in "+str(num_changed)+" spots")
            
            #delete global_index with and global_entities refering to old one

            deletename = global_entities[gid]["full_name"]
            del global_entities[gid]
            del global_index[deletename]
            if debug:
                printflush("Name "+name+" for gid:"+str(gid)+" in system ("+deletename+") so delete it along with associated index")

            ret_id = gid2
            success = True
        else:        
            #here either name = global_entiteis[gid]['full_name'] , 
            #or name equal to neither in which case default to keeping 1..
            num_changed = 0
            
            for i,gr in enumerate(global_relations):
                for e,g in enumerate(global_relations[gr]['relations']):                    
                    if g['term1_id'] == gid2 or g['term2_id'] == gid2:
                        if debug:
                            #printflush("Found gid: "+str(gid2)+" so change it to "+str(gid))
                            #printflush(g)
                            printflush(".")
                        if g['term1_id'] == gid2:
                            global_relations[gr]['relations'][e]['term1_id'] = gid
                        else:
                            global_relations[gr]['relations'][e]['term2_id'] = gid
                        num_changed = num_changed + 1
            if debug:
                printflush("Changed from old gid to new one in "+str(num_changed)+" spots")
            
            #delete global_index with and global_entities refering to old one

            deletename = global_entities[gid2]["full_name"]
            del global_entities[gid2]
            del global_index[deletename]
            if debug:
                printflush("Name "+name+" for gid:"+str(gid2)+" in system ("+deletename+") so delete it along with associated index")
                
            ret_id = gid
            success = True
            if global_entities[gid]['full_name'] != name:
                if debug:
                    printflush("Name passed in: "+name+" is not equal to global entities found: "+global_entities[gid]['full_name'])
                    printflush("thus rename global entities to "+name)
                    global_entities[gid]['full_name'] = name
                                           
    except:
        if debug:
            printflush("There was an error merging so abort!")
    
    return [success,ret_id]


# In[ ]:

#x = entity_edges[13]['edges']
#xf = [ (v[v.keys()[0]],v.keys()[0]) for v in x]
#most_assocatied_with_garnet_coleman = sorted(xf, reverse=True)
#for k in most_assocatied_with_garnet_coleman[0:200]:
#    ee = global_entities[k[1]]
#    print ee["full_name"] + "("+ee["entity_type"]+", "+str(k[1])+") - "+str(k[0])+" times"


#NOW MAKE delete, and merged based on manipulating json_output ( to see if it goes faster! )

#THIS IS BASED ON OLD GLOBAL_RELATIONS AS OPPOSED TO json_output
#function to delete an entity which is bullshit, 
#          delete from global index, but also delete any relations which have that gid as a source or target!
#need to re-run generate_json to update things global json we save
def delete_global_entity_json(gid,text,debug=False):
    #make them pass both text and gid as verification
    success = False
    if debug:
        printflush("In Delete Entity with gid:"+str(gid)+" and text:" + text)
        printflush("Counter shows # of relations: "+str(entity_edges[gid]["counter"]))
    try:
        if global_entities[gid]['full_name'] != text:
            printflush("Entity corresponding to gid: "+str(gid)+" "+global_entities[gid]['full_name']+" not equal to "+text+" so abort") 
        else:
            #delete from global_index, global_entities and delete from relations
            del global_index[text]
            del global_entities[gid]
            num_deleted = 0
            
            for i, gr in enumerate(json_output["elements"]["edges"]):
                for n,g in enumerate(gr["inst"]):
                    if g['data']['source'] == gid or g['data']['target'] == gid:                        
                        if debug:
                            printflush("Found gid: "+str(gid)+" so delete the following which includes it")
                            printflush(g)
                        del gr["inst"][n]
                        num_deleted = num_deleted + 1                    
            
            if debug:
                printflush("Delete successfull.  Deleted "+str(num_deleted)+" relations")
            
            if num_deleted != entity_edges[gid]["counter"]:
                printflush("Possible error since num deleted not equal to counter of entity, so don't delete entity_counter")
            else:
                del entity_edges[gid]
                
            success = True
    except:
        if debug:
            printflush("Error in looking for "+str(gid)+" in global_entities.  Delete "+text+" aborted")
    
    return success


#function to merge two entities which are the same, and give them a common name (which can be equal to either or new)
#          keep id of one of the two, rename that id to common name, 
#          and change all relations which have deleted id to the one kept between the two
def merge_global_entities_json(gid,gid2,name,debug=False):
    
    success = False
    ret_id = -1
    #TODO: add timer stuff here ( cause it takes for god damn ever ) and keep track of relations you merged
    #TODO: add which ever name you remove to the alias array for the object !!   VERY IMPORTANT
         
    
    if debug:
        printflush("In Merge global entitites: "+str(gid)+" and "+str(gid2)+" and keep/change to name "+name)
        #TODO: change this so that it renames id which appears less frequently cause this takes too long
        #HERE, do this (maybe) and then do adding alias thing (maybe)
        
    name = raw_input("Are you sure you want to merge "+str(gid)+" and "+str(gid)+": y/n")
    if name == "n":
        return [success,ret_id]
    
    try:
        #first figure out which entity to keep
        
        
        #first change entity id for one you aren't keeping to the one you are keeping in relations
        #then delete global_index and global_entities objects refering to old one        
        #then change name if necessary
        
        
        #here either name = global_entiteis[gid]['full_name'] , 
        #or name equal to neither in which case default to keeping 1..
        num_changed = 0

        for i,gr in enumerate(global_relations):
            for e,g in enumerate(global_relations[gr]['relations']):                    
                if g['term1_id'] == gid2 or g['term2_id'] == gid2:
                    if debug:
                        #printflush("Found gid: "+str(gid2)+" so change it to "+str(gid))
                        #printflush(g)
                        printflush(".")
                    if g['term1_id'] == gid2:
                        global_relations[gr]['relations'][e]['term1_id'] = gid
                    else:
                        global_relations[gr]['relations'][e]['term2_id'] = gid
                    num_changed = num_changed + 1
        if debug:
            printflush("Changed from old gid to new one in "+str(num_changed)+" spots")

        #delete global_index with and global_entities refering to old one

        deletename = global_entities[gid2]["full_name"]
        del global_entities[gid2]
        del global_index[deletename]
        if debug:
            printflush("Name "+name+" for gid:"+str(gid2)+" in system ("+deletename+") so delete it along with associated index")

        ret_id = gid
        success = True
        if global_entities[gid]['full_name'] != name:
            if debug:
                printflush("Name passed in: "+name+" is not equal to global entities found: "+global_entities[gid]['full_name'])
                printflush("thus rename global entities to "+name)
                global_entities[gid]['full_name'] = name
                                           
    except:
        if debug:
            printflush("There was an error merging so abort!")
    
    return [success,ret_id]


# In[156]:

retreive_from_backup()  #I NEED TO FIX THIS SO IT DOES A COPY INSTEAD OF PASS BY REFERENCE, SAME WITH make_backup


# In[157]:

def print_json_relations_summary():
    o = json_output   #this is the global output generated by generate_nodes_json
    print "Found Nodes: " + str(len(o["elements"]["nodes"]))
    print "Total Edges: "+ str(total)
    print "Found Unique Edges: " + str(len(o["elements"]["edges"]))

    p = o["elements"]["edges"]   #get edges
    newlist = sorted(p, key=lambda k: k['data']['source'])    #sort so that all entities are in order on left
    curmongo = 0
    for i,nono in enumerate(newlist):
        if curmongo != nono['data']['inst'][0]['mongoid']:
            print "\nmongo: "+str(nono['data']['inst'][0]['mongoid']) + " - "+url_list[nono['data']['inst'][0]['mongoid']]['url']
            curmongo = nono['data']['inst'][0]['mongoid']

        print "\t"+str(i)+": " + global_entities[nono['data']['source']]['full_name']+"("                               + global_entities[nono['data']['source']]['entity_type']+" "+str(nono['data']['source'])+") - "                               + global_entities[nono['data']['target']]['full_name']+"("                               + global_entities[nono['data']['target']]['entity_type']+" "+str(nono['data']['target'])+") .. count:"                               + str(len(nono['data']['inst']))+""


start = time.clock()

#MAKE SUBSET FOR TESTING
make_backup()    
#retreive_from_backup()

test_size = 4
global_relations_sub = {}
for i,gr in enumerate(global_relations):
    if i < test_size:
        global_relations_sub[gr] = global_relations[gr]

 
check = rename_global_entity(802,"budget-writing Appropriations Committee",True)    ##HOW TO RENAME ENTITIES
if check == False:
    printflush("ERROR WITH RENAMING ENTITY")

#MERGE:   TSU(ORGANIZATION 316)   and Texas Southern University(ORGANIZATION 204), delete gid2
gid = 204
gid2 = 316
name = "Texas Southern University"
#check2, ret_id2 = merge_global_entities(gid,gid2,name,True)    ##HOW TO MERGE
#if check2 == False:
#    printflush("Error with merging "+str(gid)+" and "+str(gid2)+" with name: "+name)

#MERGE:   House(ORGANIZATION 185)  and House of Representatives(ORGANIZATION 298), 
gid = 185
gid2 = 298
name = "Texas House of Representatives"   #since name equals neither, this defaults to deleting gid2
#check3, ret_id3 = merge_global_entities(gid,gid2,name,True)    ##HOW TO MERGE
#if check3 == False:
#    printflush("Error with merging "+str(gid)+" and "+str(gid2)+" with name: "+name)
    
#DELETE Texans(ORGANIZATION 262)
gid = 262
text = "Texans"
#check4 = delete_global_entity(gid,text,True)
#if check4 == False:
#    printflush("Error with deleting gid: "+str(gid)+", text: "+text)
    
generate_url_list()
generate_json()
print_json_relations_summary()

end = time.clock()
elapsed = end - start
print "**************************************"
print "Elapsed Time: "+str(elapsed)+" seconds"
print "******"


#VERIFY FINDINGS AND START KEEPING TRACK OF WHAT TO CHANGE   
#Houston Democrat, Democratic, Democrat, Democrats, 
#DELETE: Texas, Texans, 
#MERGE: House, House of Representatives
#MERGE: Texas Southern University and TSU

#Regent Bill King(PERSON 1097)  .. add Regent
#Burt Solomons ... Rep. Burt Solomons, R-Carrollton   # Put in Prior Legislatures!
#Warren Chisum(208), doesn't exist already? Rep. Warren Chisum, R-Pampa:   #probably prior legislature but check


#START HERE WHEN YOU GET BACK!


# In[142]:

#global_entities[13]


# In[ ]:




# In[ ]:




# In[ ]:




# In[407]:

text_snippets[0]


# In[409]:

from elasticsearch import Elasticsearch
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from math import log


def get_idf(word):
    es = Elasticsearch()
    q = {'query': {'bool': {'disable_coord': True, 'must': [{'match_phrase': {'body': {'analyzer': 'analyzer_keywords', 'query': word}}}]}}}
    count = es.count(index='texnews_english',body =q)['count']
    N = es.count(index='texnews_english')['count']
    #print "count: "+str(N)
    #print word,count
    return log(float(N)/(1+count))

def get_keywords(documents, min_freq=10.0, min_ngrams = 1, max_ngrams = 3):   
    
    minf = float(min_freq)/len(documents)
    tfidf_v = CountVectorizer(ngram_range=(min_ngrams,max_ngrams),stop_words = "english", min_df = minf)
    t = tfidf_v.fit_transform(documents)
    
    features = tfidf_v.get_feature_names()
    matrix = t.todense()
    keywords = {}
    
    for i in range(len(documents)):
        # Compute the norm and the weight of each feature.
        for j in range(len(features)):
            freq = matrix[i,j]

            idf = get_idf(features[j])
            tf_idf_w = idf*freq
            
            #print features[j], idf
            if features[j] in keywords:
                keywords[features[j]]+=tf_idf_w
            else:
                keywords[features[j]]=tf_idf_w
                 
    sorted_keywords = [(y,x) for (x,y) in keywords.items()]
    sorted_keywords.sort(reverse= True)

    return sorted_keywords

example = ['Diego is in favor of drug legalization', 'Diego said: "Medical Marijuana is a right', 'We believe that drug legalization could lead to the use of medical marijuana',
           'Diego is in favor of drug legalization', 'Diego said: "Medical Marijuana is a right', 'We believe that drug legalization could lead to the use of medical marijuana']

#print get_keywords(example)
print get_keywords(text_snippets)


# In[302]:

#tokenizer problem sentences
#s1 = "AUSTIN — The Texas House on Tuesday stuck a fork in the state lottery commission then resuscitated the agency hours later, realizing that dissolving it would create an unwieldy budget gap for schools and charities that depend on their piece of the pie."
#a = tokenize(s1)

#a = tokenize(fix_text(s1))  #still doesn't work

#import string
#news1 = filter(lambda x: x in string.printable, s1)
#a = tokenize(news1)
#a
for c in cur_leg:
    print c + ": "+ str(cur_leg[c])


# In[352]:

for d in db.texnews.entities.find():
    if d["party"] == "Democratic":
        print d["full_name"] + " - " + d["party"]  + ", " + d['district']


# In[3]:

i = 1
name = data[i]["full_name"]
party = data[i]["party"]
pos = "Senator"
if data[i]["chamber"] == "lower":
    pos = "Representative Rep"


# In[152]:

#from get_entities import get_entities
from elasticsearch import Elasticsearch
es = Elasticsearch()

#results = es.search(index='texnews_english',q=query,size =1,explain=True)
#results = es.search(index='texnews_english',size=10000,q=query)

#http://bitquabit.com/post/having-fun-python-and-elasticsearch-part-3/
#results = es.search(index='texnews_english',size=10000, body={'query': {'bool': {'must': [ {'match': { 'text': query }}]}}})

#results = es.search(index='texnews_english',size=10000, body={'query': {'filtered': {'filter': {'term': { 'text': query }}}}})
#this returns 0.. might need to re-index things according to 
#http://www.elasticsearch.org/guide/en/elasticsearch/guide/current/_finding_exact_values.html

#http://www.elasticsearch.org/guide/en/elasticsearch/guide/current/match-multi-word.html
query = party + " " +pos + " " + name


query = "Republican Rep Scott Sanford"
name = "Scott Sanford"

print query
#results = es.search(index='texnews_english',size=10000, body={'query': {'match': {'text': {'query': query, 'operator':'and' }}}})
#origq = {'query':{"bool":{"disable_coord": True,"must": [ {'match_phrase': {'body': {'query': query, "minimum_should_match": "75%" }}}]}}}

origq = {"query":{"bool":{"disable_coord": True,"must": [{'match_phrase': {'body': {'query':name, 'analyzer':'analyzer_keywords' }}}],
                          "should":[{'match':{'body':{'query':'Republican Rep'}}}]}}}
results = es.search(index='texnews_english',size=10000, body=origq)
if len(results['hits']['hits']) == 0:    
    print "none found so new query: " + name
    #results = es.search(index='texnews_english',size=10000, body={'query': {'match': {'text': {'query': query, 'operator':'and' }}}})
    newq = {"query":{"bool":{"disable_coord": True,"must": [{'match_phrase':{'body':{'query':name,'analyzer':'analyzer_keywords'}}}]}}}
    results = es.search(index='texnews_english',size=10000, body=newq)

    
#"minimum_should_match": "75%"    
    
print len(results['hits']['hits'])


# In[154]:

#query = "Scott Sanford"
#query = "Penny Todd"
#results = es.search(index='texnews_spanish',size=10000, body={'query': {'bool': {'must': {'match': { 'body': query }}}}})
#results = es.search(index='texnews_spanish',size=10000, body={"query":{"bool":{"disable_coord": True,"must": [{'match_phrase':{'body':{'query':query,'analyzer':'analyzer_keywords'}}}]}}})

print len(results['hits']['hits'])
print results['hits']['hits'][0]


# In[158]:

ress = results['hits']['hits']
for x in ress:
    #print x
    if '_source' in x:
        r = x['_source']        
        start = 0
        if 'body' in r:
            loc = r['body'].find(query,start)
            if loc > -1:
                print "*** Full found: " + r['date'] + ", " + r['section'] + " ," + r['title'] + " ," + r['article-num']
                print "\t"+r['body'][loc-10:loc+len(query)]
            else:
                loc = r['body'].find(name,start)
                if loc > -1:
                    print "*** Name found at spot( "+str(loc)+" of "+str(len(r['body']))+" ): " + r['date'] + ", " + r['section'] + " ," + r['title'] + " ," + r['article-num']
                    #print "\t"+r['text'][loc-10:loc+len(query)]
                    #print r['text'][start:loc].split(" ")
                    temp = r['body']


# In[93]:

#https://github.com/LuminosoInsight/python-ftfy
#!easy_install ftfy


# In[7]:

ress = results['hits']['hits'][0:1]
r = ress[0]['_source']
start = 0
loc = r['text'].find(name,start)
#print "*** Name found at spot( "+str(loc)+" of "+str(len(r['text']))+" ): " + r['date'] + ", " + r['section'] + " ," + r['title'] + " ," + r['article-num']
print "*** Name found at spot( "+str(loc)+" of "+str(len(r['text']))+" ): " + r['url'] + " ," + r['article-num']

#approach1
#sentences = ress[0]['_source']['text'].split(".\n")   #gives 15 sentences while there are more

#approach2
#http://stackoverflow.com/questions/25735644/python-regex-for-splitting-text-into-sentences-sentence-tokenizing
#import re
#sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', ress[0]['_source']['text'])  
#this approach is better than first and gives 37 sentences

#approach3
#http://stackoverflow.com/questions/9474395/how-to-break-up-a-paragraph-by-sentences-in-python
#from nltk import tokenize
#sentences = tokenize.sent_tokenize(ress[0]['_source']['text'])  
#gives 34 and is slower than second, but maybe we can include things to not tokenize for sentences (Lt. , Gov. , Rep.)

#approach4
#http://stackoverflow.com/questions/14095971/how-to-tweak-the-nltk-sentence-tokenizer
#from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters
#punkt_param = PunktParameters()
#punkt_param.abbrev_types = set(['lt', 'gov', 'rep', 'mrs', 'mr', 'inc'])
#sentence_splitter = PunktSentenceTokenizer(punkt_param)
#text = ress[0]['_source']['text'].replace('?"', '? "').replace('!"', '! "').replace('."', '. "')
#sentences = sentence_splitter.tokenize(text)
#this is probably the best approach since you can send in specific abbreviations.
#however we need to fix weird quotes to normal quotes to get part of it to work as expected
#for that we look at ftfy above .. maybe we can incorporate that.

#approach 5 ( hopefully improved on approach4)
from __future__ import unicode_literals
from ftfy import fix_text
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters
punkt_param = PunktParameters()
punkt_param.abbrev_types = set(['lt', 'gov', 'rep', 'mrs', 'mr', 'inc'])
sentence_splitter = PunktSentenceTokenizer(punkt_param)
text = fix_text(ress[0]['_source']['text']).replace('?"', '? "').replace('!"', '! "').replace('."', '. "')
sentences = sentence_splitter.tokenize(text)
#approach 5 WORKS THE BEST!!

c = 0
for s in sentences:
    print str(c) + ": "+ s 
    c = c + 1


# In[9]:

#*** Name found at spot( 1185 of 3963 ): 2009-04-02, news/falkenberg ,Lawmaker needs course in Medicaid 101 ,1735774
#prior_context = temp[start:loc+1].split(" ")[-20:-1]
#post_context = temp[loc:len(temp)-1].split(" ")[0:20]
#print " ".join(prior_context) + " " + " ".join(post_context)

#print temp[start:loc] #+ " " + post_context
#print "****"+temp[loc:(loc + len(name))]+"****" + temp[(loc+len(name)):]


# In[11]:

n = 0
for r in results['hits']['hits']: 
    if n < 80 and r["_score"] > .2:
        if query in r["_source"]["text"]:
            print "\n***found "+query+" with score: "+str(r["_score"]) + "\n" #+" in "+r["_source"]["text"] + "\n"
            text = ''.join([i if ord(i) < 128 else '' for i in r["_source"]["text"]])
            
            #before anything look for name in text  
            end = len(text)
            start = 0
            while start < end:
                loc = text.find(query,start)
                if loc == -1:
                    start = end
                    start = loc + len(query)
                else:
                    print "found at "+str(loc)+"\n"
                    print text[loc-10:loc+len(query)]
                    #print text[start:loc].rsplit(" ",1)[-1]
                
                
            #tokens = tokenize(text)
            #print tokens
            
            #entities = ner.extract_entities(tokens)
            
            #for e in entities:
                #range = e[0]
                #tag = e[1]
                #score = e[2]
                #score_text = "{:0.3f}".format(score)
                #entity_text = " ".join(tokens[i] for i in range)
                #print "\tScore: " + score_text + ": " + tag + ": " + entity_text
        n = n + 1        
print str(n)+" results found"





# In[132]:

#results['hits']['hits'][8217]

#results['hits']['hits'][8258]

#results['hits']['hits'][8319]

#results['hits']['hits'][357]


# In[363]:

#https://gist.github.com/troyane/c9355a3103ea08679baf
from nltk.tag.stanford import NERTagger
import nltk

nerpath = "/Users/dolano/htdocs/dama-larca/stanford-ner/stanford-ner-2015-01-30/"
st = NERTagger(nerpath+"classifiers/english.all.3class.distsim.crf.ser.gz", nerpath+'stanford-ner.jar')

#print st.tag('Gov. Rick Perry unexpectedly canceled plans to visit areas hit by a massive Central Texas wildfire.\nA Perry spokeswoman said the governor\'s scheduled visit on Saturday of damaged areas in Bastrop County near Austin, as well as his participation in a news conference with local and state officials, did not take place because of "logistical issues" with Perry arriving in Bastrop on time.\nPerry\'s office on Friday had announced the governor would visit the area.\nPerry spokeswoman Allison Castle said the governor was in Austin and was keeping in regular contact with officials on the wildfire.\nCastle did not say when Perry would return to Bastrop. Perry visited the area earlier this week after he cut short a presidential campaign trip to deal with the crisis.'.split())
tagged = st.tag('Gov. Rick Perry unexpectedly canceled plans to visit areas hit by a massive Central Texas wildfire.\nA Perry spokeswoman said the governor\'s scheduled visit on Saturday of damaged areas in Bastrop County near Austin, as well as his participation in a news conference with local and state officials, did not take place because of "logistical issues" with Perry arriving in Bastrop on time.\nPerry\'s office on Friday had announced the governor would visit the area.\nPerry spokeswoman Allison Castle said the governor was in Austin and was keeping in regular contact with officials on the wildfire.\nCastle did not say when Perry would return to Bastrop. Perry visited the area earlier this week after he cut short a presidential campaign trip to deal with the crisis.'.split())
#tagged1 = st.tag("With his Republican primary victory safely behind him, Texas Gov. Rick Perry is still working hard to court conservative voters.  Perry made a guest appearance Saturday night at an event in Tyler hosted by conservative radio and television talk-show host Glenn Beck.  Speculation is swirling that Perry may consider a run for president in 2012 and experts say appearing with Beck keeps the governor in the minds of conservative voters. Perry has denied he's considering a run.  Perry calls Beck a national leader with a powerful message about Washington and its out of control spending. Perry is running for a third term as governor. He faces former Houston Mayor Bill White, a Democrat, in November.".split())


# In[365]:

#nltk.download()
entities = nltk.chunk.ne_chunk(tagged)
tagged
#entities


# In[ ]:

#OR use java and call it
#http://stackoverflow.com/questions/18371092/stanford-named-entity-recognizer-ner-functionality-with-nltk
#java -mx1000m -cp stanford-ner.jar edu.stanford.nlp.ie.NERServer -loadClassifier classifiers/english.all.3class.distsim.crf.ser.gz -port 9191

#http://nlp.stanford.edu:8080/ner/process


# In[ ]:

#https://github.com/mit-nlp/MITIE
#comparable to Stanford - https://github.com/mit-nlp/MITIE/wiki/Evaluation
Diegos-MacBook-Pro:python dolano$ python ner.py 
loading NER model...

Tags output by this NER model: ['PERSON', 'LOCATION', 'ORGANIZATION', 'MISC']
Tokenized input: ['Gov', '.', 'Rick', 'Perry', 'unexpectedly', 'canceled', 'plans', 'to', 'visit', 'areas', 'hit', 'by', 'a', 'massive', 'Central', 'Texas', 'wildfire', '.', 'A', 'Perry', 'spokeswoman', 'said', 'the', 'governor', "'s", 'scheduled', 'visit', 'on', 'Saturday', 'of', 'damaged', 'areas', 'in', 'Bastrop', 'County', 'near', 'Austin', ',', 'as', 'well', 'as', 'his', 'participation', 'in', 'a', 'news', 'conference', 'with', 'local', 'and', 'state', 'officials', ',', 'did', 'not', 'take', 'place', 'because', 'of', '"', 'logistical', 'issues', '"', 'with', 'Perry', 'arriving', 'in', 'Bastrop', 'on', 'time', '.', 'Perry', "'s", 'office', 'on', 'Friday', 'had', 'announced', 'the', 'governor', 'would', 'visit', 'the', 'area', '.', 'Perry', 'spokeswoman', 'Allison', 'Castle', 'said', 'the', 'governor', 'was', 'in', 'Austin', 'and', 'was', 'keeping', 'in', 'regular', 'contact', 'with', 'officials', 'on', 'the', 'wildfire', '.', 'Castle', 'did', 'not', 'say', 'when', 'Perry', 'would', 'return', 'to', 'Bastrop', '.', 'Perry', 'visited', 'the', 'area', 'earlier', 'this', 'week', 'after', 'he', 'cut', 'short', 'a', 'presidential', 'campaign', 'trip', 'to', 'deal', 'with', 'the', 'crisis', '.']

Entities found: [(xrange(2, 4), 'PERSON', 1.4964058753217928), (xrange(14, 16), 'LOCATION', 0.6081528093396019), (xrange(19, 20), 'PERSON', 0.8578910868604561), (xrange(33, 35), 'LOCATION', 1.6928261371011268), (xrange(36, 37), 'LOCATION', 1.432602387519684), (xrange(64, 65), 'PERSON', 1.097299000266322), (xrange(67, 68), 'LOCATION', 1.1223108526168661), (xrange(71, 72), 'PERSON', 1.1581921796329224), (xrange(85, 86), 'PERSON', 0.9906898930002838), (xrange(87, 89), 'PERSON', 0.9442651334634773), (xrange(94, 95), 'LOCATION', 1.029676065451085), (xrange(112, 113), 'PERSON', 1.4203139855625926), (xrange(116, 117), 'LOCATION', 0.7508056193276653), (xrange(118, 119), 'PERSON', 1.3918731759656906)]

Number of entities detected: 14
   Score: 1.496: PERSON: Rick Perry
   Score: 0.608: LOCATION: Central Texas
   Score: 0.858: PERSON: Perry
   Score: 1.693: LOCATION: Bastrop County
   Score: 1.433: LOCATION: Austin
   Score: 1.097: PERSON: Perry
   Score: 1.122: LOCATION: Bastrop
   Score: 1.158: PERSON: Perry
   Score: 0.991: PERSON: Perry
   Score: 0.944: PERSON: Allison Castle
   Score: 1.030: LOCATION: Austin
   Score: 1.420: PERSON: Perry
   Score: 0.751: LOCATION: Bastrop
   Score: 1.392: PERSON: Perry


# In[31]:

import sys, os
mitiepath = "/Users/dolano/htdocs/dama-larca/mitie/MITIE-master/"
sys.path.append(mitiepath+"mitielib")

from mitie import *
from collections import defaultdict

ner = named_entity_extractor(mitiepath+'MITIE-models/english/ner_model.dat')
#tokens = tokenize(load_entire_file('../../sample_text.txt'))
tokens = tokenize("With his Republican primary victory safely behind him, Texas Gov. Rick Perry is still working hard to court conservative voters.  Perry made a guest appearance Saturday night at an event in Tyler hosted by conservative radio and television talk-show host Glenn Beck.  Speculation is swirling that Perry may consider a run for president in 2012 and experts say appearing with Beck keeps the governor in the minds of conservative voters. Perry has denied he's considering a run.  Perry calls Beck a national leader with a powerful message about Washington and its out of control spending. Perry is running for a third term as governor. He faces former Houston Mayor Bill White, a Democrat, in November.")
entities = ner.extract_entities(tokens)

for e in entities:
    range = e[0]
    tag = e[1]
    score = e[2]
    score_text = "{:0.3f}".format(score)
    entity_text = " ".join(tokens[i] for i in range)
    print "   Score: " + score_text + ": " + tag + ": " + entity_text


# In[ ]:

# Now let's run one of MITIE's binary relation detectors.  MITIE comes with a
# bunch of different types of relation detector and includes tools allowing you
# to train new detectors.  However, here we simply use one, the "person born in place" relation detector.
rel_detector = binary_relation_detector(mitiepath+"MITIE-models/english/binary_relations/rel_classifier_people.person.place_of_birth.svm")

# First, let's make a list of neighboring entities.  Once we have this list we
# will ask the relation detector if any of these entity pairs is an example of the "person born in place" relation.
neighboring_entities = [(entities[i][0], entities[i+1][0]) for i in xrange(len(entities)-1)]

# Also swap the entities and add those in as well.  We do this because "person
# born in place" mentions can appear in the text in as "place is birthplace of person".  
#So we must consider both possible orderings of the arguments.
neighboring_entities += [(r,l) for (l,r) in neighboring_entities]

# Now that we have our list, let's check each entity pair and see which one the detector selects.
for person, place in neighboring_entities:
    # Detection has two steps in MITIE. 
    #   First, you convert a pair of entities into a special representation.
    rel = ner.extract_binary_relation(tokens, person, place)
    #   Then you ask the detector to classify that pair of entities.  
    #      If the score value is > 0 then it is saying that it has found a relation.  
    #      The larger the score the more confident it is.  
    
    # Finally, the reason we do detection in two parts is so you can reuse the intermediate rel in many
    # calls to different relation detectors without needing to redo the processing done in extract_binary_relation().
    score = rel_detector(rel)
    # Print out any matching relations.
    if (score > 0):
        person_text     = " ".join(tokens[i] for i in person)
        birthplace_text = " ".join(tokens[i] for i in place)
        print person_text, "BORN_IN", birthplace_text

# The code above shows the basic details of MITIE's relation detection API.
# However, it is important to note that real world data is noisy any confusing.
# Not all detected relations will be correct.  Therefore, it's important to
# aggregate many relation detections together to get the best signal out of
# your data.  A good way to do this is to pick an entity you are in interested
# in (e.g. Benjamin Franklin) and then find all the relations that mention him
# and order them by most frequent to least frequent.  We show how to do this in
# the code below.
query = "Benjamin Franklin"
hits = defaultdict(int)

for person, place in neighboring_entities:
    rel = ner.extract_binary_relation(tokens, person, place)
    score = rel_detector(rel)
    if (score > 0):
        person_text     = " ".join(tokens[i] for i in person)
        birthplace_text = " ".join(tokens[i] for i in place)
        if (person_text == query):
            hits[birthplace_text] += 1

print "\nTop most common relations:"
for place, count in sorted(hits.iteritems(), key=lambda x:x[1], reverse=True):
    print count, "relations claiming", query, "was born in", place


# In[ ]:

Diegos-MacBook-Pro:MITIE-master dolano$ cd MITIE-models/english/binary_relations/

rel_classifier_book.written_work.author.svm
rel_classifier_film.film.directed_by.svm
rel_classifier_influence.influence_node.influenced_by.svm
rel_classifier_law.inventor.inventions.svm
rel_classifier_location.location.contains.svm
rel_classifier_location.location.nearby_airports.svm
rel_classifier_location.location.partially_contains.svm
rel_classifier_organization.organization.place_founded.svm
rel_classifier_organization.organization_founder.organizations_founded.svm
rel_classifier_organization.organization_scope.organizations_with_this_scope.svm
rel_classifier_people.deceased_person.place_of_death.svm
rel_classifier_people.ethnicity.geographic_distribution.svm
rel_classifier_people.person.ethnicity.svm
rel_classifier_people.person.nationality.svm
rel_classifier_people.person.parents.svm
rel_classifier_people.person.place_of_birth.svm
rel_classifier_people.person.religion.svm
rel_classifier_people.place_of_interment.interred_here.svm
rel_classifier_time.event.includes_event.svm
rel_classifier_time.event.locations.svm
rel_classifier_time.event.people_involved.svm


# In[ ]:

#http://nbviewer.ipython.org/github/charlieg/A-Smattering-of-NLP-in-Python/blob/master/A%20Smattering%20of%20NLP%20in%20Python.ipynb


# In[ ]:

def get_entities(article_bodies):
    for x in article_bodies:
        for (_,lista) in get_entities(x['_source']['body'],'es').items():
            for entity in lista:
                if entity in all_entities_freq:
                    all_entities_freq[entity]+=1
                else:
                    all_entities_freq[entity]=1

    print all_entities_freq
    print ' '
    ranking = sorted(all_entities_freq.items(),key=lambda x: x[1],reverse= True)
    print ranking[0:20]


# In[199]:

#Coreference resolution 
#https://groups.google.com/forum/#!topic/nltk-users/g1MsgI2PxXU

#https://code.google.com/p/nltk-drt/

get_ipython().system(u'easy_install linearlogic')

