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
import ConfigParser

from bson.json_util import dumps
from bson.objectid import ObjectId

from dto.response.classes.base import Base
from dto.response.utils.baseutils import BaseUtils
from dto.response.classes.listinglist import ListingList


from persistence.mongodatabase import mongoDatabase


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

get_listing_api = Blueprint('get_listing_api', __name__)


@get_listing_api.route('/listings/<listingid>', methods = ['GET'])
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
        print traceback.format_exc()

    jsonObj = jsonpickle.encode(reponseObj, unpicklable=False)
    response = Response(jsonObj)
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS, GET')
    return response