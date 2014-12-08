# flask imports
from flask import Flask
from flask import request
from flask import Response
from flask import Blueprint

import traceback

# json handling
import jsonpickle
import json
from bson.json_util import dumps
from bson.objectid import ObjectId

from business.implementations.implementations import Implementations

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

newImplementation = Implementations()

concierge_email_api = Blueprint('concierge_email_api', __name__)

@concierge_email_api.route('/conciergeEmail', methods = ['POST'])
def sendEmailConcierge():

    reponseObj = Base()
    json_object = request.form.keys()
    json_resquest = json.loads(json_object[0])
    # json_resquest = request.form

    try:
        email = json_resquest["email"]
        name = json_resquest["name"]
        phone = json_resquest["phone"]
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