import os
import re
import datetime
import traceback
import numpy
import math
import json
import traceback
import ConfigParser
import datetime

from operator import itemgetter

from business.utils.twilioutils import TwilioUtils

# flask imports
from flask import Flask
from flask import request, abort
from flask import Response
from flask import Blueprint

# json handling
import jsonpickle
import ConfigParser

from bson.json_util import dumps
from bson.objectid import ObjectId

from dto.response.classes.base import Base
from dto.response.classes.object import Object
from dto.response.utils.baseutils import BaseUtils
from dto.response.classes.preference import Preference

from persistence.mongodatabase import mongoDatabase

from persistence.collections.users import Users
from persistence.collections.preferences import Preferences
from persistence.collections.listingowners import ListingOwners
from persistence.collections.calibrations import Calibrations


# load constants
# MONGO_URL = 'mongodb://jhon:1234@dogen.mongohq.com:10080/app31803464'
# MONGO_DB = "app31803464"
# MONGO_URL = "mongodb://jhon:1234@kahana.mongohq.com:10066/app30172457"
# MONGO_DB = "app30172457"

# TODO: improve the way this vars are loaded
# load constants
config = ConfigParser.ConfigParser()
config.read("config.cfg")
mongo_section = 'mongo_config'
MONGO_URL = config.get(mongo_section, 'url')
MONGO_DB = config.get(mongo_section, 'db')

# init db connection
myDB = mongoDatabase(MONGO_URL)
db = myDB.getDB(MONGO_DB)

save_preferences_api = Blueprint('save_preferences_api', __name__)

@save_preferences_api.route('/calibrations/test', methods=['POST'])
def create_calibration_test():
    try:
        test_instance = TestData()
        test_instance.load_calibrations_test_data()
        return Response()
    except Exception as e:
        print "There was an unexpected error: " , str(e)
        print traceback.format_exc()
        abort(500)

@save_preferences_api.route('/calibrations', methods=['POST'])
def calculate_calibration():
    try:
        # get parameters from args
        budget = int(request.form['budget'])
        city = request.form['city']
        bedrooms = int(request.form['bedrooms'])

        if (budget is not None) and (city is not None) and (bedrooms is not None):
            ## get calibration value
            calibrations_collection_obj = Calibrations(db)
            calibration_value = calibrations_collection_obj.get_calibration_value(city, bedrooms, budget)
            json_obj = jsonpickle.encode(calibration_value, unpicklable=False)
            return Response(json_obj)
        else:
            abort(500)
    except Exception as e:
        print "There was an unexpected error: " , str(e)
        print traceback.format_exc()
        abort(500)

@save_preferences_api.route('/preferences', methods=['POST'])
def save_preferences():
    try:
        # get parameters from form
        fullname = request.form['fullname']
        email = request.form['email']
        phone = request.form['phone']
        budget = request.form['budget']
        bedrooms = request.form['bedrooms']
        city = request.form['city']

        # build user object to be stored in the database
        user_object = {'fullname': fullname, 'email': email, 'phone': phone}

        ## save user in the database
        user_collection_obj = Users(db)
        user_id = user_collection_obj.save_user(user_object)

        # build preference object to be stored in the database
        preference_object = {'user_id': user_id, 'budget': budget, 'bedrooms': bedrooms, 'city': city}

        ## save preference in the database
        preference_collection_obj = Preferences(db)
        preference_collection_obj.save_preference(preference_object)

        # get listing owners from database
        listing_owners_collection_obj = ListingOwners(db)
        retrieved_listing_owners = listing_owners_collection_obj.gell_all_listing_owners()

        print retrieved_listing_owners

        ## TODO: send broadcast to twilio
        twilio_instance = TwilioUtils()
        twilio_instance.send_broadcast_to_listing_owners()

        return Response()
    except Exception as e:
        print "There was an unexpected error: " , str(e)
        print traceback.format_exc()
        abort(500)

## old method
@save_preferences_api.route('/userpreferences/<email>', methods = ['POST'])
def saveUserPreferences(email):
    reponseObj = Base()

    try:
        filtersObj = {}

        ## identify filters
        f = request.form
        if 'filters' in f:
            print "request.form['filters']" , request.form['filters']
            filtersObj = jsonpickle.decode(request.form['filters'])
            print "type(filtersObj)" , type(filtersObj)
            print "filtersObj" , filtersObj


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
        unit_must_have["rooms"]=[]

        for field in request.form:
            print field
            preferencesStr = request.form[field]
            if preferencesStr:
                if field in ["Locales_good", "Parks", "Walkable", "Family", "Student_vibe", "Young_pro", "Quiet", "Classic", "Modern"]:
                    hood_delighter["keywords"].append(field)

                elif field in ["Near_action", "Safe", "Easy_transport", "Parking"]:
                    hood_must_have["keywords"].append(field)

                elif field in ["hardwood", "laundry", "lighting", "deck_balcony", "cieling", "kitchen", "spacing", "ameneties", "view", "modern", "classic", "loft"]:
                    unit_delighter["keywords"].append(field)

                elif field in ["pet", "spacing", "lighting", "parking"]:
                    unit_must_have["keywords"].append(field)

                elif field == "sublet_roomate":
                    unit_must_have["rooms"].extend((1,2,3,4,5))
                    unit_must_have["keywords"].append("sublet_roomate")
                elif field == "studio":
                    unit_must_have["rooms"].extend((0,1,2))
                    unit_must_have["keywords"].append("studio")
                elif field == "1bed":
                    unit_must_have["rooms"].append(1)
                elif field == "2bed":
                    unit_must_have["rooms"].append(2)

                elif field in ["firstname", "lastname", "email", "gender", "move_reason", "location", "transportation", "profession", "importance", "movein"]:
                    information[field] = preferencesStr

                elif field in ["budget", "walking_time", "bike_time", "driving_time", "transit_time"]:
                    information[field] = int(preferencesStr)

        if 'budget' not in information.keys():
            information['budget'] = 5000

        db_dict["information"] = information
        db_dict["filters"] = filtersObj
        db_dict["unit_must_have"] = unit_must_have
        db_dict["unit_delighter"] = unit_delighter
        db_dict["hood_must_have"] = hood_must_have
        db_dict["hood_delighter"] = hood_delighter

        preferencesCollection = db['preferences']
        pref_id = preferencesCollection.insert(db_dict)
        print "pref_id" , pref_id
        reponseObj.Data = Preference(jsonpickle.decode(dumps(pref_id)), filtersObj)
        #reponseObj.Data = {"preferenceId" : pref_id}

        # fromadd = "concierge@socrex.com"
        # toadd = information["email"]
        # msg = MIMEMultipart()
        # msg['From'] = fromadd
        # msg['To'] = toadd
        # msg['Subject'] = "Socrex - Concierge reply"
        # body = "Thank you for using our service, to view your personalized listings please follow this url:\n \nhttp://frontend-socrex-stage.herokuapp.com/#/listings/filter/"+str(pref_id)
        # msg.attach(MIMEText(body, 'plain'))

        # # Send the message via our own SMTP server, but don't include the
        # # envelope header.
        # s = smtplib.SMTP('smtp.gmail.com:587')
        # s.ehlo()
        # s.starttls()
        # s.ehlo()
        # s.login(fromadd, "monaco123")
        # text = msg.as_string()
        # s.sendmail(fromadd, toadd, text)
        # s.quit()


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