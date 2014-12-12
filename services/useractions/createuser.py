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

from persistence.collections.listings import Listings


# load constants
# MONGO_URL = 'mongodb://jhon:1234@dogen.mongohq.com:10080/app31803464'
# MONGO_DB = "app31803464"
MONGO_URL = "mongodb://jhon:1234@kahana.mongohq.com:10066/app30172457"
MONGO_DB = "app30172457"

# init db connection
myDB = mongoDatabase(MONGO_URL)
db = myDB.getDB(MONGO_DB)

create_user_api = Blueprint('create_user_api', __name__)

@create_user_api.route('/user', methods=['POST'])
def create_user():
    reponse_obj = Base()
    try:
        user_first_name = request.form['firstName']
        user_last_name = request.form['lastName']
        user_email = request.form['email']
        user_phone = request.form['phone']
        user_auth0_user_id = request.form['auth0UserId']
        user_shortlist_list = jsonpickle.decode(request.form['shortlist'])

        user_shortlist_list_object_id = []
        for user_shortlist_list_element in user_shortlist_list:
            user_shortlist_list_object_id.append(ObjectId(user_shortlist_list_element))

        users_collection = db['users']
        listings_collection = db['listings']

        shortlist_listings_cursors = listings_collection.find({"_id" : {"$in" : user_shortlist_list_object_id}})
        shortlist_listings_list = list(shortlist_listings_cursors)

        user_obj = {
            'firstname': user_first_name,
            'lastname': user_last_name,
            'email': user_email,
            'phone': user_phone,
            'auth0userid': user_auth0_user_id,
            'comments': [],
            'shortlist': shortlist_listings_list,
            'applylist': []
        }

        return_user_id = users_collection.insert(user_obj)

        reponse_obj.Data = jsonpickle.decode(dumps({'UserId': return_user_id}))

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
