from dama_globals import *
from dama_utils import *
from pymongo import MongoClient

if __name__ == '__main__':
	if len(sys.argv) > 1:
		searchfor = sys.argv[1]
		if searchfor == "confirmed":
			conn = MongoClient()
			db = conn.newsdb
			#save_legislators_to_from_mongo(db)
			remove_inactive_active_people(db)
		print "DONE"
	else:
		print 'You must add "confirmed" (no quotes) in order to delete inactive conflicts from the entities db'
