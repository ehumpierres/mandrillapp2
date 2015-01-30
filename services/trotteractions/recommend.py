# flask imports
from flask import Flask
from flask import request
from flask import Response
from flask import Blueprint

import traceback

# json handling
import jsonpickle
import ConfigParser

from bson.json_util import dumps
from bson.objectid import ObjectId

from dto.response.classes.base import Base
from dto.response.utils.baseutils import BaseUtils

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

recommend_api = Blueprint('recommend_api', __name__)

@recommend_api.route('/recommend', methods=['POST'])
def recommend():
    reponse_obj = Base()
    try:
        print request.form
        request_listing = request.form['listingid']
        request_user = request.form['email']
        # request_trotter = request.form['trotterid']

        listingsCollection = db['listings']
        usersCollection = db['users']
        # trottersCollection = db['trotters']

        user = usersCollection.find_one({"email" : request_user})
        listing = listingsCollection.find_one({"_id" : ObjectId(request_listing)})
        print user
        print listing
        # trotter = listingsCollection.find_one({"_id" : ObjectId(request_trotter)})

        listing['recommended'] = 1
        listing['status'] = 'not verified'

        shortlist = user['shortlist']
        shortlist.append(listing)

        usersCollection.update({'_id':user['_id']}, {'$set':{'shortlist':shortlist}})

        reponse_obj.Data = jsonpickle.decode(dumps({'_id': user['_id']}))
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
