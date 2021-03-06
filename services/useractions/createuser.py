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

from persistence.collections.listings import Listings

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

        users_collection = db['users']
        listings_collection = db['listings']

        #validate existing user
        user = users_collection.find_one({'email': user_email})
        print "user" , user

        return_user_id = None
        # TODO: fix this, the idea is not wo overwrite the shortlist. This is suposed to be done in front end, further auth0 info is required.
        if user is None:

            user_shortlist_list_object_id = []
            for user_shortlist_list_element in user_shortlist_list:
                user_shortlist_list_object_id.append(ObjectId(user_shortlist_list_element))



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
        else:
            return_user_id = user['_id']

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
