import os
import re
import datetime
import traceback
import numpy
import math
import json
import traceback
import types
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

from persistence.utils.mongoutils import MongoUtils


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

get_listing_details_api = Blueprint('get_listing_details_api', __name__)


@get_listing_details_api.route('/listings/details', methods = ['POST'])
def get_listings_details_by_id_list_method():

    reponse_obj = Base()

    try:
        listings_id_list = jsonpickle.decode(request.form['listings_id_list'])
        print "listings_id_list" , listings_id_list
        ## select mondodb collection
        listingsCollection = db['listings']

        listings_object_id_list = MongoUtils.to_object_id(listings_id_list)
        result_listings_cursors = listingsCollection.find({'_id': {'$in': listings_object_id_list}})
        result_listings_list = list(result_listings_cursors)

        reponse_obj.Data = jsonpickle.decode(dumps(result_listings_list))
        BaseUtils.SetOKDTO(reponse_obj)
        # TODO: IMPLEMENT APROPIATE ERROR HANDLING
    except Exception as e:
        BaseUtils.SetUnexpectedErrorDTO(reponse_obj)
        print "There was an unexpected error: ", str(e)
        print traceback.format_exc()

    json_obj = jsonpickle.encode(reponse_obj, unpicklable=False)
    response = Response(json_obj)
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS, GET')
    return response