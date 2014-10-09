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

		filtersStr = request.form['id']
		filtersStr = int(filtersStr)

		#filtersDic = jsonpickle.decode(filtersStr)

		preferencesCollection = db['preferences']

		entry = preferencesCollection.find_one({"information.EntryId" : filtersStr})

		information = entry["information"]
		unit_delighter = entry["unit_delighter"]
		unit_must_have = entry["unit_must_have"]
		hood_delighter = entry["hood_delighter"]
		hood_must_have = entry["hood_must_have"]
		delimiters = []
		udelighters = []
		if "keywords" in unit_delighter:
			udelighters = unit_delighter["keywords"]

		if "keywords" in unit_must_have:
			umust_haves = unit_must_have["keywords"]

		listingsCollection = db['listings']

		bed_range = []
		for i in range(1,4):
			field = "apt_type"+str(i)
			if field in unit_must_have:
				if unit_must_have[field] == "2bed":
					bed_range.append(2)
				elif unit_must_have[field] == "1bed":
					bed_range.append(1)
				elif unit_must_have[field] == "studio":
					#Add case for studio			
					bed_range.append(-1)
					bed_range.append(0)
					bed_range.append(1)
				else:
					# Add case for roomate
					bed_range.append(-2)
					bed_range.append(0)
					bed_range.append(1)

		if -2 not in bed_range:
			delimiters.append("roommate")
			delimiters.append("by the room")
		if -1 not in bed_range:
			delimiters.append("studio")
		if -2 or 2 not in bed_range:
			delimiters.append("bedrooms")
			delimiters.append("bathrooms")

		# bedroom price filter

		filteredListingsCursors = listingsCollection.find(
			{
				"price": {"$in": range(800,information["budget"])}
				, "bedroom": {"$in": bed_range}
			}
		)
		filteredListingsList = list(filteredListingsCursors)  

		

		deleted = False
		final_filter = []
		print delimiters

		for listing in filteredListingsList:
			if delimiters:
				delim = "|".join(delimiters)
				if not re.search(delim, listing["body"], flags=re.IGNORECASE):
					# if re.search(regex, listing["body"], flags=re.IGNORECASE):
					listing["score"] = 0
					for regex in udelighters:
						if re.search(regex, listing["body"], flags=re.IGNORECASE):
							listing["score"] += 10
					price = float(information["budget"] - listing["price"]) / float(information["budget"])
					price_score = price * 150.00
					listing["score"] += price_score
					final_filter.append(listing)
			else: 
				listing["score"] = 0
				for regex in udelighters:
					if re.search(regex, listing["body"], flags=re.IGNORECASE):
						listing["score"] += 10
				price = float(information["budget"] - listing["price"]) / float(information["budget"])
				price_score = price * 150.00
				listing["score"] += price_score
				final_filter.append(listing)


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
							if field_number == 1045:
								unit_delighter["keywords"].append("hardwood")
							elif field_number == 1046:
								unit_delighter["keywords"].append("laundry in")
							elif field_number == 1047:
								unit_delighter["keywords"].append("good light") 
								unit_delighter["keywords"].append("lighting")
							elif field_number == 1048:
								unit_delighter["keywords"].append("roof deck")
								unit_delighter["keywords"].append("balcony")
							elif field_number == 1049:
								unit_delighter["keywords"].append("high cielings")
								unit_delighter["keywords"].append("spacious")
							elif field_number == 1050:
								unit_delighter["keywords"].append("renovated kitchen")
								unit_delighter["keywords"].append("modern kitchen")
							elif field_number == 1051:
								unit_delighter["keywords"].append("huge")
								unit_delighter["keywords"].append("walk-in closet")
								unit_delighter["keywords"].append("storage space")
							elif field_number == 1052:
								unit_delighter["keywords"].append("gym")
								unit_delighter["keywords"].append("pool")
							elif field_number == 1053:
								unit_delighter["keywords"].append("view")
								unit_delighter["keywords"].append("skyline")
								unit_delighter["keywords"].append("waterfront")
							elif field_number == 1054:
								unit_delighter["keywords"].append("modern")
								unit_delighter["keywords"].append("new")
								unit_delighter["keywords"].append("renovated")
								unit_delighter["keywords"].append("newly")
							elif field_number == 1055:
								unit_delighter["keywords"].append("cieling windows")
								unit_delighter["keywords"].append("fireplace")
								unit_delighter["keywords"].append("french doors")
							elif field_number == 1056:
								unit_delighter["keywords"].append("loft")


							# db_field = "unit_d"+str(unit_count_d)
							# unit_count_d += 1
							# unit_delighter[db_field] = preferencesStr
					#Get Unit Must-haves
					elif field_number in range (1145,1152):
						if unit_count_m < 4:
							db_field = "unit_m"+str(unit_count_m)
							unit_count_m += 1
							unit_must_have[db_field] = preferencesStr
					# Get apt type
					elif field_number == 635:
						db_field = "apt_type"+str(apt_type_count)
						unit_count_m += 1
						unit_must_have[db_field] = "sublet"
						unit_must_have["keywords"].append("roomate")
					elif field_number == 434:
						db_field = "apt_type"+str(apt_type_count)
						unit_count_m += 1
						unit_must_have[db_field] = "studio"
						unit_must_have["keywords"].append("studio")
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
		body = "Thank you for using our service, to view your personalized listings please follow this url:\n \nhttp://socrex-frontend.gopagoda.com/app/#/view2/"+str(information["EntryId"])
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
	
@app.route('/listings/sendemail', methods = ['POST'])
def sendEmailToContact():
    
    reponseObj = Base()
    
    try:
    	## instantiate email sender object
        mailSenderObj = MailSender('smtp.gmail.com', 587, 'jhon@socrex.com' , '123456789@Socrex')
        ## send email
        mailSenderObj.sendEmail('jhon@socrex.com','jhonjairoroa87@gmail.com','subject test' , 'subject body')
        ## email quit sender object
        mailSenderObj.quit()
        ## add ok code to dto
        BaseUtils.SetOKDTO(reponseObj)
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
    
@app.route('/listings/sendemail', methods = ['POST'])
def sendEmailToContact():
    
    reponseObj = Base()
    
    try:
    	## instantiate email sender object
        mailSenderObj = MailSender('smtp.gmail.com', 587, 'jhon@socrex.com' , '123456789@Socrex')
        ## send email
        mailSenderObj.sendEmail('jhon@socrex.com','jhonjairoroa87@gmail.com','subject test' , 'subject body')
        ## email quit sender object
        mailSenderObj.quit()
        ## add ok code to dto
        BaseUtils.SetOKDTO(reponseObj)
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
	hostip = os.environ['IP']
	hostport = int(os.environ['PORT'])
	app.run(host=hostip,port=hostport)
	# enable to run in heroku
	#app.run()
