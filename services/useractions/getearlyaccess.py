# flask imports
from flask import Flask
from flask import request
from flask import Response
from flask import Blueprint

import traceback
import ConfigParser

# json handling
import jsonpickle
import json

from business.utils.mandrillutils import MandrillUtils

from dto.response.classes.base import Base
from dto.response.utils.baseutils import BaseUtils

from persistence.mongodatabase import mongoDatabase
from persistence.collections.earlyaccesses import EarlyAccesses


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

get_early_access_api = Blueprint('get_early_access_api', __name__)

@get_early_access_api.route('/getearlyaccess', methods = ['POST'])
def get_early_access():

    response_obj = Base()

    try:

        full_name = request.form["fullname"]
        email = request.form["email"]
        phone = request.form["phone"]

        # build object to be stored in the database
        early_access_object = {'fullname': full_name, 'email': email, 'phone': phone}

        ## save early access in the database
        early_access_collection_obj = EarlyAccesses(db)
        early_access_collection_obj.save_early_access(early_access_object)

        ## send email through mandrill to the user
        mandrill_instance = MandrillUtils()
        mandrill_instance.send_early_access_template_to_user(early_access_object['fullname'], early_access_object['email'])

        ## send email notification to trotter
        mandrill_instance.send_early_access_notification_template_to_trotter(early_access_object['fullname'], early_access_object['email'], early_access_object['phone'],)
        BaseUtils.SetOKDTO(response_obj)

    # TODO: IMPLEMENT APROPIATE ERROR HANDLING
    except Exception as e:
        BaseUtils.SetUnexpectedErrorDTO(response_obj)
        print "There was an unexpected error: ", str(e)
        print traceback.format_exc()

    json_obj = jsonpickle.encode(response_obj, unpicklable=False)
    response = Response(json_obj)
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS, GET')
    return response