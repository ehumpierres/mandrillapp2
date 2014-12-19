# flask imports
from flask import Flask
from flask import request
from flask import Response
from flask import Blueprint

import traceback
import datetime

# json handling
import jsonpickle
from bson.json_util import dumps
from bson.objectid import ObjectId

from dto.response.classes.base import Base
from dto.response.utils.baseutils import BaseUtils

from persistence.mongodatabase import mongoDatabase

from business.implementations.implementations import Implementations
from persistence.collections.neighborhoods import Neighborhoods

# load constants
# MONGO_URL = 'mongodb://jhon:1234@dogen.mongohq.com:10080/app31803464'
# MONGO_DB = "app31803464"
MONGO_URL = "mongodb://jhon:1234@kahana.mongohq.com:10066/app30172457"
MONGO_DB = "app30172457"

# init db connection
myDB = mongoDatabase(MONGO_URL)
db = myDB.getDB(MONGO_DB)

newImplementation = Implementations()


add_listing_api = Blueprint('add_listing_api', __name__)

def update_neighborhood_info(listing_id, neighborhoods_coords):
    newImplementation.update_neighborhood_info(listing_id, neighborhoods_coords)

def get_neighborhood_coordinates():
    neighborhood_collection_persistence = Neighborhoods(db)
    # get all neighborhoods coords
    neighborhoods_coordinates = neighborhood_collection_persistence.get_neighborhoods_coordinates()
    return neighborhoods_coordinates

def cast_save_listing_form(request_form):
    cast_obj = dict()
    request_form_keys = request_form.keys()

    #  copy elements to new obt
    for request_form_key in request_form_keys:
        cast_obj[request_form_key] = request_form[request_form_key]

    #  set right types
    cast_obj['bathrooms'] = int(cast_obj['bathrooms'])
    cast_obj['bedrooms'] = int(cast_obj['bedrooms'])
    cast_obj['latitude'] = float(cast_obj['latitude'])
    cast_obj['longitude'] = float(cast_obj['longitude'])
    cast_obj['price'] = int(cast_obj['price'])
    cast_obj['pictures'] = jsonpickle.decode(request_form['pictures'])
    cast_obj['lastupdated'] = datetime.datetime.utcnow().isoformat()
    return cast_obj


# create a single listing
@add_listing_api.route('/listings', methods=['POST'])
def save_listing():
    reponse_obj = Base()
    try:
        request_form = request.form
        listing_dic = cast_save_listing_form(request_form)

        # get all neighborhoods coords
        neighborhoods_coords = get_neighborhood_coordinates()
        # save listing in database
        saved_listing_id = newImplementation.save_listing(listing_dic)
        # update listing neighborhood info
        update_neighborhood_info(saved_listing_id, neighborhoods_coords)
        # prepare object to be responded
        reponse_obj.Data = jsonpickle.decode(dumps({'_id': saved_listing_id}))
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
