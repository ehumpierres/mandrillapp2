import os
import re
import datetime

# flask imports
from flask import Flask
from flask import request
from flask import Response
#from flask.ext.cors import CORS
#from flask.ext.mongoengine import MongoEngine


# json handling
import jsonpickle
from bson.json_util import dumps
from bson.objectid import ObjectId


# dto response objects
from dto.response.classes.base import Base
from dto.response.classes.listinglist import ListingList
# dto response utils
from dto.response.utils.baseutils import BaseUtils

from persistence.mongodatabase import mongoDatabase


# load constants
MONGO_URL = "mongodb://jhon:1234@kahana.mongohq.com:10066/app30172457"
MONGO_DB = "app30172457"

# init db connection
myDB = mongoDatabase(MONGO_URL)
db = myDB.getDB(MONGO_DB)


# init flask app
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'
	
## TODO: THIS HAS TO BE A GET METHOD
@app.route('/listings/filter', methods = ['POST'])
def filterListings():
	
	filtersStr = request.form['filters']
	filtersDic = jsonpickle.decode(filtersStr)
	
	listingsCollection = db['listings']
	
	filteredListingsCursors = listingsCollection.find(filtersDic, { "body": 0, "title":0 , "description":0, "feetype":0})
	
	# returns the list of data objects
	filteredListingsList = list(filteredListingsCursors)  
	
	reponseObj = Base()
	reponseObj.Data = ListingList(3,jsonpickle.decode(dumps(filteredListingsList)),10)
	BaseUtils.SetOKDTO(reponseObj)	
	
	jsonObj = jsonpickle.encode(reponseObj, unpicklable=False)
	
	response = Response(jsonObj)
		
	return response

@app.route('/listings/<listingid>', methods = ['GET'])
def getListingById(listingid= None):
	
	reponseObj = Base()
	
	try:
		if listingid is not None:
			## select mondodb collection
			listingsCollection = db['listings']
			## retrieve listing from db
			listingsObject = listingsCollection.find_one({'_id': ObjectId(listingid)})
			## serialize listing
			reponseObj.Data = jsonpickle.decode(dumps(listingsObject))
			BaseUtils.SetOKMessageDTO(reponseObj)	
	# TODO: IMPLEMENT APROPIATE ERROR HANDLING
   	except :
   		BaseUtils.SetUnexpectedErrorDTO(reponseObj)
       	print "There was an unexpected error: "
		
	jsonObj = jsonpickle.encode(reponseObj, unpicklable=False)
	response = Response(jsonObj)		
	return response
	

if __name__ == '__main__':
	app.debug = True 
	#hostip = os.environ['IP']
	#hostport = int(os.environ['PORT'])
	#app.run(host=hostip,port=hostport)
	app.run()