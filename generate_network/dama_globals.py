#GLOBAL VARS
class GlobalObjs:
	def __init__(self):
		self.global_entities = []
		self.global_relations = {}
		self.article_relations = {}
		self.global_index = {}
		self.json_output = {"elements":{"nodes":[],"edges":[]}}
		self.edges_seen = []      #just used to see whether an edge has already been added
		self.text_snippets = []   #keeps track of text snippets
		self.entity_edges = {}    #used as lookup to see how many edges an entity has and where they are located.
		self.url_texts = {}       #quick look up for the sentences in an article
		self.url_list = {}	  #indexed by number mongourls
		self.larger_relations = {}  #larger network info goes here
	
globalobjs = GlobalObjs()

#def global_entities():
#	global globalobjs;
#	return globalobjs.global_entities


global_entities = globalobjs.global_entities
global_relations = globalobjs.global_relations
article_relations = globalobjs.article_relations
global_index = globalobjs.global_index
json_output = globalobjs.json_output
edges_seen = globalobjs.edges_seen
text_snippets = globalobjs.text_snippets
entity_edges = globalobjs.entity_edges
url_texts = globalobjs.url_texts
url_list = globalobjs.url_list
larger_relations = globalobjs.larger_relations
