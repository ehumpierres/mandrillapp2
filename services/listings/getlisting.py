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
from dto.response.classes.listinglist import ListingList


from persistence.mongodatabase import mongoDatabase


# load constants
# MONGO_URL = 'mongodb://jhon:1234@dogen.mongohq.com:10080/app31803464'
# MONGO_DB = "app31803464"
MONGO_URL = "mongodb://jhon:1234@kahana.mongohq.com:10066/app30172457"
MONGO_DB = "app30172457"

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