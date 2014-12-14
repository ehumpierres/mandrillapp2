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
# MONGO_URL = 'mongodb://jhon:1234@dogen.mongohq.com:10080/app31803464'
# MONGO_DB = "app31803464"
MONGO_URL = "mongodb://jhon:1234@kahana.mongohq.com:10066/app30172457"
MONGO_DB = "app30172457"

# init db connection
myDB = mongoDatabase(MONGO_URL)
db = myDB.getDB(MONGO_DB)

validate_user_api = Blueprint('validate_user_api', __name__)

@validate_user_api.route('/user/validate/<userauth0id>', methods=['GET'])
def validate_user(userauth0id= None):
    reponse_obj = Base()
    try:
        if userauth0id is not None:

            usersCollection = db['users']

            user = usersCollection.find_one({"auth0userid" : userauth0id})

            user_id = None
            if user is not None:
                user_id = user['_id']

            reponse_obj.Data = jsonpickle.decode(dumps({'UserId': user_id}))
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
