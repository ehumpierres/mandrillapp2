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

create_user_email_api = Blueprint('create_user_email_api', __name__)

@create_user_email_api.route('/createUserEmail', methods = ['POST'])
def send_email_create_user():

    reponseObj = Base()
    # json_object = request.form.keys()
    # json_resquest = json.loads(json_object[0])
    # # json_resquest = request.form

    try:

        # if "phone" in json_resquest.keys():
        #     phone = json_resquest["phone"]
        # else: 

        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        name = firstname + " " + lastname
        email = request.form["email"]
        phone = request.form["phone"]
        movein = request.form["movein"]
        budget = request.form["budget"]
        filtersObj = request.form['filters']

        isSuccessful = newImplementation.sendEmailCreateUser(name, phone, email, movein, budget, filtersObj)
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