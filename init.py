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
	reponseObj = Base()
	try:

		filtersStr = request.form['filters']
		filtersDic = jsonpickle.decode(filtersStr)
	
		listingsCollection = db['listings']
	
		filteredListingsCursors = listingsCollection.find(filtersDic, { "body": 0, "title":0 , "description":0, "feetype":0})
	
		# returns the list of data objects
		filteredListingsList = list(filteredListingsCursors)  
	
		reponseObj.Data = ListingList(3,jsonpickle.decode(dumps(filteredListingsList)),10)
		BaseUtils.SetOKDTO(reponseObj)	
	# TODO: IMPLEMENT APROPIATE ERROR HANDLING
	except Exception as e:
   		BaseUtils.SetUnexpectedErrorDTO(reponseObj)
	       	print "There was an unexpected error: " , str(e)
	
	jsonObj = jsonpickle.encode(reponseObj, unpicklable=False)
	response = Response(jsonObj)
	response.headers.add('Access-Control-Allow-Origin', '*')
	response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS, GET')  
	return response

@app.route('/preferences', methods = ['POST'])
def savePreferences():	
	reponseObj = Base()
	try:
		hood_must_have = dict()
		hood_delighter = dict()
		unit_must_have = dict()
		unit_delighter = dict()
		information = dict()
		db_dict = dict()
		unit_count_m = 1
		hood_count_m = 1
		unit_count_d = 1
		hood_count_d = 1
		apt_type_count = 1

		for field in request.form:
			preferencesStr = request.form[field]
			if preferencesStr:
				if field[:5] == "Field":
					field_number = field[5:]
					field_number = int(field_number)
					# Get hood Delighters
					if field_number in range (843,855):
						if hood_count_d < 4:
							db_field = "hood_d"+str(hood_count_d)
							hood_count_d += 1
							hood_delighter[db_field] = preferencesStr
					# Get hood Must-haves
					elif field_number in range (943,949):
						if hood_count_m < 4:
							db_field = "hood_m"+str(hood_count_m)
							hood_count_m += 1
							hood_must_have[db_field] = preferencesStr
					#Get Unit Delighters
					elif field_number in range (1045,1057):
						if unit_count_d < 4:
							db_field = "unit_d"+str(unit_count_d)
							unit_count_d += 1
							unit_delighter[db_field] = preferencesStr
					#Get Unit Must-haves
					elif field_number in range (1145,1152):
						if unit_count_m < 4:
							db_field = "unit_m"+str(unit_count_m)
							unit_count_m += 1
							unit_must_have[db_field] = preferencesStr
							print unit_must_have[db_field]
					# Get apt type
					elif field_number == 635:
						db_field = "apt_type"+str(apt_type_count)
						unit_count_m += 1
						unit_must_have[db_field] = "room"
					elif field_number == 434:
						db_field = "apt_type"+str(apt_type_count)
						unit_count_m += 1
						unit_must_have[db_field] = "studio"
					elif field_number == 535:
						db_field = "apt_type"+str(apt_type_count)
						unit_count_m += 1
						unit_must_have[db_field] = "1bed"
					elif field_number == 735:
						db_field = "apt_type"+str(apt_type_count)
						unit_count_m += 1
						unit_must_have[db_field] = "2bed"
					# Gather relevant informaion
					elif field_number == 1:
						information["firstname"] = preferencesStr
					elif field_number == 2: 
						information["lastname"] = preferencesStr
					elif field_number == 5:
						information["email"] = preferencesStr
					elif field_number == 1248:
						information["gender"] = preferencesStr
					elif field_number == 316:
						information["move_reason"] = preferencesStr
					elif field_number == 1247:
						information["importance"] = preferencesStr
					elif field_number == 325:
						information["location"] = preferencesStr
					elif field_number == 836:
						information["transportation"] = preferencesStr
					elif field_number == 321:
						information["budget"] = preferencesStr
					elif field_number == 319:
						information["movein"] = preferencesStr
				elif field == "EntryId":
					information["EntryId"] = preferencesStr
				elif field == "DateUpdated":
					information["DateUpdated"] = preferencesStr
				elif field == "DateCreated":
					information["DateCreated"] = preferencesStr

		db_dict["information"] = information
		db_dict["unit_must_have"] = unit_must_have
		db_dict["unit_delighter"] = unit_delighter
		db_dict["hood_must_have"] = hood_must_have
		db_dict["hood_delighter"] = hood_delighter

		preferencesCollection = db['preferences']
		preferencesCollection.insert(db_dict)
	
		BaseUtils.SetOKDTO(reponseObj)	
	# TODO: IMPLEMENT APROPIATE ERROR HANDLING
	except Exception as e:
   		BaseUtils.SetUnexpectedErrorDTO(reponseObj)
	       	print "There was an unexpected error: " , str(e)
	
	jsonObj = jsonpickle.encode(reponseObj, unpicklable=False)
	response = Response(jsonObj)
	response.headers.add('Access-Control-Allow-Origin', '*')
	response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS, GET')  
	return response

"""
def filterListings():
	response = Response(jsonObj)
	try:
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
	except :
   		BaseUtils.SetUnexpectedErrorDTO(reponseObj)
	       	print "There was an unexpected error: "
	

	response.headers.add('Access-Control-Allow-Origin', '*')
	response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS, GET')  
	return response
"""

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
   	except Exception as e:
   		BaseUtils.SetUnexpectedErrorDTO(reponseObj)
	       	print "There was an unexpected error: " , str(e)
		
	jsonObj = jsonpickle.encode(reponseObj, unpicklable=False)
	response = Response(jsonObj)	
	response.headers.add('Access-Control-Allow-Origin', '*')
	response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS, GET')  	
	return response
	

if __name__ == '__main__':
	app.debug = True 
	#hostip = os.environ['IP']
	#hostport = int(os.environ['PORT'])
	#app.run(host=hostip,port=hostport)
	app.run()
