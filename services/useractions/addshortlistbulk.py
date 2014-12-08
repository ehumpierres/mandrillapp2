# flask imports
from flask import Flask
from flask import request
from flask import Response
from flask import Blueprint

import traceback

# json handling
import jsonpickle
from bson.json_util import dumps
from bson.objectid import ObjectId

from dto.response.classes.base import Base
from dto.response.utils.baseutils import BaseUtils

from persistence.mongodatabase import mongoDatabase


# load constants
MONGO_URL = 'mongodb://jhon:1234@dogen.mongohq.com:10080/app31803464'
MONGO_DB = "app31803464"
# MONGO_URL = "mongodb://jhon:1234@kahana.mongohq.com:10066/app30172457"
# MONGO_DB = "app30172457"

# init db connection
myDB = mongoDatabase(MONGO_URL)
db = myDB.getDB(MONGO_DB)

add_bulk_shortlist_api = Blueprint('add_bulk_shortlist_api', __name__)

@add_bulk_shortlist_api.route('/shortlistbulk', methods=['POST'])
def add_bulk_shortlist():
    reponse_obj = Base()
    try:
        request_listings = request.form['listingids']
        request_user = request.form['userid']

        request_listings_split = request_listings.split(',')

        bulklistings = []
        for r_listing in request_listings_split:
            bulklistings.append(ObjectId(r_listing))

        print bulklistings

        listingsCollection = db['listings']
        usersCollection = db['users']

        user = usersCollection.find_one({"_id" : ObjectId(request_user)})
        listings_result = listingsCollection.find({"_id" : {"$in" : bulklistings}})

        listings = list(listings_result)

        print listings

        shortlist = user['shortlist']
        for listing in listings:
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
