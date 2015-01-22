import os
import re
import datetime
import traceback
import numpy
import math
import json
import traceback
import datetime

from operator import itemgetter

# flask imports
from flask import Flask
from flask import request
from flask import Response
from flask import Blueprint

# json handling
import jsonpickle
from bson.json_util import dumps
from bson.objectid import ObjectId

from dto.response.classes.base import Base
from dto.response.utils.baseutils import BaseUtils
from dto.response.classes.preference import Preference


from persistence.mongodatabase import mongoDatabase


# load constants
# MONGO_URL = 'mongodb://jhon:1234@dogen.mongohq.com:10080/app31803464'
# MONGO_DB = "app31803464"
MONGO_URL = "mongodb://jhon:1234@kahana.mongohq.com:10066/app30172457"
MONGO_DB = "app30172457"

# init db connection
myDB = mongoDatabase(MONGO_URL)
db = myDB.getDB(MONGO_DB)

save_preferences_api = Blueprint('save_preferences_api', __name__)


@save_preferences_api.route('/userpreferences', methods = ['POST'])
def saveUserPreferences():
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