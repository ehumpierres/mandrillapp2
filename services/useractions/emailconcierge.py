# flask imports
from flask import Flask
from flask import request
from flask import Response
from flask import Blueprint

import traceback

# json handling
import jsonpickle
import json
import ConfigParser

from bson.json_util import dumps
from bson.objectid import ObjectId

from business.implementations.implementations import Implementations

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

newImplementation = Implementations()

concierge_email_api = Blueprint('concierge_email_api', __name__)

@concierge_email_api.route('/conciergeEmail', methods = ['POST'])
def sendEmailConcierge():

    reponseObj = Base()
    json_object = request.form.keys()
    json_resquest = json.loads(json_object[0])
    # json_resquest = request.form

    try:

        # if "phone" in json_resquest.keys():
        #     phone = json_resquest["phone"]
        # else: 
        userid = json_resquest["userid"]
        usersCollection = db['users']
        user = usersCollection.find_one({"_id" : ObjectId(userid)})
        phone = user["phone"]
        firstname = user["firstname"]
        lastname = user["lastname"]
        email = user["email"]
        name = firstname + " " + lastname

        listingurl = json_resquest["listingurl"]
        listingid = json_resquest["listingid"]
        request_type = json_resquest["request_type"]

        



        isSuccessful = newImplementation.sendEmailConcierge(email, name, phone, listingurl, listingid, request_type)
        if isSuccessful:
            BaseUtils.SetOKDTO(reponseObj)
        else:
            ## todo: implement code for not nullable listingid or  useremail
            BaseUtils.SetUnexpectedErrorDTO(reponseObj)
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