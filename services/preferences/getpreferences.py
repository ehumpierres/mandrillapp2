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

get_preferences_api = Blueprint('get_preferences_api', __name__)


@get_preferences_api.route('/userpreferences/<userPreferencesId>', methods = ['GET'])
def getUserPreferences(userPreferencesId= None):
    reponseObj = Base()
    # {"apartmentType":"1 Bedroom" , "personType":"student","hoodType":"classic", "budget":5000, "moveIn":20143101}

    try:
        if(userPreferencesId != None):
            preferencesCollection = db['preferences']
            pref_obj = preferencesCollection.find_one({"_id": ObjectId(userPreferencesId)})
            print pref_obj
            filtersObj = dict()
            if "filters" in pref_obj.keys():
                filtersObj = pref_obj['filters']
            reponseObj.Data = Preference(jsonpickle.decode(dumps(pref_obj['_id'])), filtersObj)
            print "reponseObj.Data" , reponseObj.Data
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