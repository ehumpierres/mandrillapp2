import os
import re
import datetime
import traceback

# flask imports
from flask import Flask
from flask import request
from flask import Response
#from flask.ext.cors import CORS
#from flask.ext.mongoengine import MongoEngine

from operator import itemgetter

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

# Import smtplib for the actual sending function
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

from business.utils.mailsender import MailSender
from business.implementations.implementations import Implementations


# load constants
MONGO_URL = "mongodb://jhon:1234@kahana.mongohq.com:10066/app30172457"
MONGO_DB = "app30172457"

# init db connection
myDB = mongoDatabase(MONGO_URL)
db = myDB.getDB(MONGO_DB)
newImplementation = Implementations()


# init flask app
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'


# Filter entries based off of user preferences

@app.route('/listings/filter', methods = ['POST'])
def filterListings():	
	reponseObj = Base()
	try:

		filtersStr = request.form['id']
		filtersStr = int(filtersStr)

		#filtersDic = jsonpickle.decode(filtersStr)

		preferencesCollection = db['preferences']
		listingsCollection = db['listings']
		hoodsCollection = db['hoods']


		entry = preferencesCollection.find_one({"information.EntryId" : filtersStr})

		information = entry["information"]
		unit_delighter = entry["unit_delighter"]
		unit_must_have = entry["unit_must_have"]
		hood_delighter = entry["hood_delighter"]
		hood_must_have = entry["hood_must_have"]

		delimiters = []

		if "rooms" in unit_must_have.keys():
			bed_range = unit_must_have["rooms"]
		else:
			bed_range = range(0,4)

		udelighters = []
		if "keywords" in unit_delighter.keys():
			udelighters = unit_delighter["keywords"]

		umust_haves = []
		if "keywords" in unit_must_have.keys():
			umust_haves = unit_must_have["keywords"]

		hmust_haves = []
		if "keywords" in hood_must_have.keys():
			hmust_haves = hood_must_have["keywords"]

		hdelighters = []
		if "keywords" in hood_delighter.keys():
			hdelighters = hood_delighter["keywords"]

		unit_query = {
					"price": {"$in": range(800,information["budget"])}
					, "bedroom": {"$in": bed_range}
				}
		for must_have in umust_haves:
			unit_query[must_have] = 1
			print unit_query[must_have]


		filteredListingsCursors = listingsCollection.find(unit_query)
		filteredListingsList = list(filteredListingsCursors)

		final_filter = []

		for listing in filteredListingsList:

			listing_hood = listing["neighborhood"]
			hood_query = {'_id': ObjectId(listing_hood["_id"])}
			hood = hoodsCollection.find_one(hood_query)
			passed_musthaves = True
			print hmust_haves
			for must_have in hmust_haves:
				if hood[must_have] != 1:
					passed_musthaves = False
			if passed_musthaves:
				listing["score"] = 0
				print udelighters
				for delighter in udelighters:
					if listing[delighter] == 1:
						listing["score"] += 20
				print hdelighters
				for delighter in hdelighters:
					if hood[delighter] == 1:
						listing["score"] += 20

				price = float(information["budget"] - listing["price"]) / float(information["budget"])
	 			price_score = price * 150.00
 				listing["score"] += price_score
 				final_filter.append(listing)





		# deleted = False
		# final_filter = []
		# print delimiters

		# for listing in filteredListingsList:
		# 	if delimiters:
		# 		delim = "|".join(delimiters)
		# 		if not re.search(delim, listing["body"], flags=re.IGNORECASE):
		# 			# if re.search(regex, listing["body"], flags=re.IGNORECASE):
		# 			listing["score"] = 0
		# 			for regex in udelighters:
		# 				if re.search(regex, listing["body"], flags=re.IGNORECASE):
		# 					listing["score"] += 10
		# 			price = float(information["budget"] - listing["price"]) / float(information["budget"])
		# 			price_score = price * 150.00
		# 			listing["score"] += price_score
		# 			final_filter.append(listing)
		# 	else: 
		# 		listing["score"] = 0
		# 		for regex in udelighters:
		# 			if re.search(regex, listing["body"], flags=re.IGNORECASE):
		# 				listing["score"] += 10
		# 		price = float(information["budget"] - listing["price"]) / float(information["budget"])
		# 		price_score = price * 150.00
		# 		listing["score"] += price_score
		# 		final_filter.append(listing)


		finalList = sorted(final_filter, key=itemgetter('score'), reverse=True)
	
		# returns the list of data objects
	
		reponseObj.Data = ListingList(3,jsonpickle.decode(dumps(finalList)),10)
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



# Capture User preferences call (Wufoo form for now)

@app.route('/preferences', methods = ['POST'])
def savePreferences():	
	reponseObj = Base()
	try:
		hood_must_have = dict()
		hood_must_have["keywords"] = []
		hood_delighter = dict()
		hood_delighter["keywords"] = []
		unit_must_have = dict()
		unit_must_have["keywords"] = []
		unit_delighter = dict()
		unit_delighter["keywords"] = []
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
							if field_number == 843:
								hood_delighter["keywords"].append("Locales_good")
							elif field_number == 844:
								hood_delighter["keywords"].append("Parks")
							elif field_number == 845:
								hood_delighter["keywords"].append("Walkable")
							elif field_number == 847:
								hood_delighter["keywords"].append("Family")
							elif field_number == 848:
								hood_delighter["keywords"].append("Student_vibe")
							elif field_number == 849:
								hood_delighter["keywords"].append("Young_pro")
							elif field_number == 850:
								hood_delighter["keywords"].append("Quiet")
							elif field_number == 852:
								hood_delighter["keywords"].append("Classic")
							elif field_number == 854:
								hood_delighter["keywords"].append("Modern")

					# Get hood Must-haves
					elif field_number in range (943,947):
						if hood_count_m < 4:
							if field_number == 943:
								hood_must_have["keywords"].append("Near_action")
							elif field_number == 944:
								hood_must_have["keywords"].append("Safe")
							elif field_number == 945:
								hood_must_have["keywords"].append("Easy_transport")
							elif field_number == 946:
								hood_must_have["keywords"].append("Parking")

					#Get Unit Delighters
					elif field_number in range (1045,1057):
						if unit_count_d < 4:
							if field_number == 1045:
								unit_delighter["keywords"].append("hardwood")
							elif field_number == 1046:
								unit_delighter["keywords"].append("laundry")
							elif field_number == 1047:
								unit_delighter["keywords"].append("lighting") 
							elif field_number == 1048:
								unit_delighter["keywords"].append("deck_balcony")
							elif field_number == 1049:
								unit_delighter["keywords"].append("cieling")
							elif field_number == 1050:
								unit_delighter["keywords"].append("kitchen")
							elif field_number == 1051:
								unit_delighter["keywords"].append("spacing")
							elif field_number == 1052:
								unit_delighter["keywords"].append("ameneties")
							elif field_number == 1053:
								unit_delighter["keywords"].append("view")
							elif field_number == 1054:
								unit_delighter["keywords"].append("modern")
							elif field_number == 1055:
								unit_delighter["keywords"].append("classic")
							elif field_number == 1056:
								unit_delighter["keywords"].append("loft")

					#Get Unit Must-haves
					elif field_number in range (1145,1151):
						if unit_count_m < 4:
							if field_number == 1145:
								unit_must_have["keywords"].append("pet")
							elif field_number == 1146:
								unit_must_have["keywords"].append("spacing")
							elif field_number == 1147:
								unit_must_have["keywords"].append("lighting")
							elif field_number == 1150:
								unit_must_have["keywords"].append("parking")
					# Get apt type
					elif field_number == 635:
						unit_must_have["rooms"] = range(1,5)
						unit_must_have["keywords"].append("sublet_roomate")
					elif field_number == 434:
						unit_must_have["rooms"] = range(0,2)
						unit_must_have["keywords"].append("studio")
					elif field_number == 535:
						unit_must_have["rooms"] = [1]
					elif field_number == 735:
						unit_must_have["rooms"] = [2]
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
					elif field_number == 1250:
						information["location"] = preferencesStr
					elif field_number == 836:
						information["transportation"] = preferencesStr
					elif field_number == 321:
						budget = preferencesStr.split(".")
						information["budget"] = int(budget[0])
					elif field_number == 319:
						information["movein"] = preferencesStr
				elif field == "EntryId":
					information["EntryId"] = int(preferencesStr)
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

		fromadd = "concierge@socrex.com"
		toadd = information["email"]
		msg = MIMEMultipart()
		msg['From'] = fromadd
		msg['To'] = toadd
		msg['Subject'] = "Socrex - Concierge reply"
		body = "Thank you for using our service, to view your personalized listings please follow this url:\n \nhttp://frontend-socrex-stage.herokuapp.com/#/listings/filter/"+str(information["EntryId"])
		msg.attach(MIMEText(body, 'plain'))

		# Send the message via our own SMTP server, but don't include the
		# envelope header.
		s = smtplib.SMTP('smtp.gmail.com:587')
		s.ehlo()
		s.starttls()
		s.ehlo()
		s.login(fromadd, "monaco123")
		text = msg.as_string()
		s.sendmail(fromadd, toadd, text)
		s.quit()

	
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
	
@app.route('/listing/<listingid>/user/<useremail>/sendemail', methods = ['POST'])
def sendEmailToContact(listingid= None, useremail=None ):
    
    reponseObj = Base()
    
    try:
    	isSuccessful = newImplementation.sendEmailToContact(listingid, useremail)
    	if isSuccessful:
    		BaseUtils.SetOKDTO(reponseObj)
    	else:
    		## todo: implement code for not nullable listingid or  useremail
    		BaseUtils.SetUnexpectedErrorDTO(reponseObj)
    # TODO: IMPLEMENT APROPIATE ERROR HANDLING
    except Exception as e:
        BaseUtils.SetUnexpectedErrorDTO(reponseObj)
        print "There was an unexpected error: " , str(e)
        print traceback.format_exc()
    
    jsonObj = jsonpickle.encode(reponseObj, unpicklable=False)
    response = Response(jsonObj)    
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS, GET')      
    return response

@app.route('/listing/<listingid>/user/<useremail>/verifyavailability', methods = ['POST'])
def verifyListingAvailability(listingid= None, useremail=None ):
    
    reponseObj = Base()
    
    try:
    	isSuccessful = newImplementation.verifyListingAvailability(listingid, useremail)
    	if isSuccessful:
    		BaseUtils.SetOKDTO(reponseObj)
    	else:
    		## todo: implement code for not nullable listingid or  useremail
    		BaseUtils.SetUnexpectedErrorDTO(reponseObj)
    # TODO: IMPLEMENT APROPIATE ERROR HANDLING
    except Exception as e:
        BaseUtils.SetUnexpectedErrorDTO(reponseObj)
        print "There was an unexpected error: " , str(e)
        print traceback.format_exc()
    
    jsonObj = jsonpickle.encode(reponseObj, unpicklable=False)
    response = Response(jsonObj)    
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS, GET')      
    return response

@app.route('/listing/<listingid>/user/<useremail>/expertreview', methods = ['POST'])
def expertReview(listingid= None, useremail=None ):
    
    reponseObj = Base()
    
    try:
    	isSuccessful = newImplementation.expertReview(listingid, useremail)
    	if isSuccessful:
    		BaseUtils.SetOKDTO(reponseObj)
    	else:
    		## todo: implement code for not nullable listingid or  useremail
    		BaseUtils.SetUnexpectedErrorDTO(reponseObj)
    # TODO: IMPLEMENT APROPIATE ERROR HANDLING
    except Exception as e:
        BaseUtils.SetUnexpectedErrorDTO(reponseObj)
        print "There was an unexpected error: " , str(e)
        print traceback.format_exc()
    
    jsonObj = jsonpickle.encode(reponseObj, unpicklable=False)
    response = Response(jsonObj)    
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS, GET')      
    return response

@app.route('/listing/<listingid>/user/<useremail>/virtualtour', methods = ['POST'])
def virtualTour(listingid= None, useremail=None ):
    
    reponseObj = Base()
    
    try:
    	isSuccessful = newImplementation.virtualTour(listingid, useremail)
    	if isSuccessful:
    		BaseUtils.SetOKDTO(reponseObj)
    	else:
    		## todo: implement code for not nullable listingid or  useremail
    		BaseUtils.SetUnexpectedErrorDTO(reponseObj)
    # TODO: IMPLEMENT APROPIATE ERROR HANDLING
    except Exception as e:
        BaseUtils.SetUnexpectedErrorDTO(reponseObj)
        print "There was an unexpected error: " , str(e)
        print traceback.format_exc()
    
    jsonObj = jsonpickle.encode(reponseObj, unpicklable=False)
    response = Response(jsonObj)    
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS, GET')      
    return response

if __name__ == '__main__':
	app.debug = True 
	# enable to run in cloud9
	#hostip = os.environ['IP']
	#hostport = int(os.environ['PORT'])
	#app.run(host=hostip,port=hostport)
	# enable to run in heroku
	app.run()
