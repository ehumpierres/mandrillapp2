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

change_status_api = Blueprint('change_status_api', __name__)

@change_status_api.route('/changestatus', methods=['POST'])
def change_status():
    reponse_obj = Base()
    try:
        request_listing = request.form['listingId']
        request_user = request.form['userId']
        request_status = request.form['status']

        usersCollection = db['users']

        user = usersCollection.find_one({"_id" : ObjectId(request_user)})

        shortlist = user['shortlist']
        result_bool = False

        for entry in shortlist:
            if entry['_id'] == ObjectId(request_listing):
                entry['status'] = request_status
                print entry['status']
                result_bool = True

        usersCollection.update({'_id':user['_id']}, {'$set':{'shortlist':shortlist}})

        reponse_obj.Data = jsonpickle.decode(dumps({'result': result_bool}))
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
