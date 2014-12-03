import os
import re
import datetime
import traceback
import numpy
import math
import json
import traceback
import datetime

from operator import itemgetter

# flask imports
from flask import Flask
from flask import request
from flask import Response
from flask import Blueprint

# json handling
import jsonpickle
from bson.json_util import dumps
from bson.objectid import ObjectId

from dto.response.classes.base import Base
from dto.response.utils.baseutils import BaseUtils
from dto.response.classes.listinglist import ListingList


from persistence.mongodatabase import mongoDatabase


# load constants
# MONGO_URL = 'mongodb://jhon:1234@dogen.mongohq.com:10080/app31803464'
# MONGO_DB = "app31803464"
MONGO_URL = "mongodb://jhon:1234@kahana.mongohq.com:10066/app30172457"
MONGO_DB = "app30172457"

# init db connection
myDB = mongoDatabase(MONGO_URL)
db = myDB.getDB(MONGO_DB)

filter_listings_api = Blueprint('filter_listings__api', __name__)


@filter_listings_api.route('/listings/filter', methods = ['POST'])
def filterListings():
    reponseObj = Base()
    try:

        requestId = request.form['id']

        if "currentPage" in request.form.keys():
            requestPage = request.form['currentPage']
            requestPage = int(requestPage)
        else:
            requestPage = 1
        if "itemsOnPage" in request.form.keys():
            requestItems = request.form['itemsOnPage']
            requestItems = int(requestItems)
        else:
            requestItems = 100

        limitNumber = (requestPage-1) * requestItems
        skipNumber = requestPage * requestItems

        preferencesCollection = db['preferences']
        listingsCollection = db['listings']
        hoodsCollection = db['hoods']

        print "requestId" , requestId
        entry = preferencesCollection.find_one({"_id" : ObjectId(requestId)})

        information = entry["information"]
        unit_delighter = entry["unit_delighter"]
        unit_must_have = entry["unit_must_have"]
        hood_delighter = entry["hood_delighter"]
        hood_must_have = entry["hood_must_have"]

        delimiters = []

        if "rooms" in unit_must_have.keys():
            bed_range = unit_must_have["rooms"]

        if len(bed_range) == 0:
            bed_range = range(0,4)

        udelighters = []
        if "keywords" in unit_delighter.keys():
            udelighters = unit_delighter["keywords"]

        umust_haves = []
        if "keywords" in unit_must_have.keys():
            umust_haves = unit_must_have["keywords"]

        hmust_haves = []
        if "keywords" in hood_must_have.keys():
            hmust_haves = hood_must_have["keywords"]

        hdelighters = []
        if "keywords" in hood_delighter.keys():
            hdelighters = hood_delighter["keywords"]

        unit_query = {
                    "price": {"$in": range(300,information["budget"])}
                    , "bedroom": {"$in": bed_range}
                    , "isDeleted": 0
                }
        if "studio" in umust_haves:
            unit_query["studio"] = 1
        if "sublet_roomate" in umust_haves:
            unit_query["sublet_roomate"] = 1
        else:
            unit_query["sublet_roomate"] = 0

        filteredListingsCursors = listingsCollection.find(unit_query)
        filteredListingsList = list(filteredListingsCursors)

        final_filter = []
        score_list = []
        price_list = []

        for listing in filteredListingsList:

            ldatetime=""
            idatetime=""

            if "neighborhood" in listing.keys():
                listing_hood = listing["neighborhood"]
                hood = listing_hood
                ldatetime = datetime.datetime.strptime(listing["move_in"], '%Y%d%m')
                idatetime = datetime.datetime.strptime(information["movein"], '%Y%m%d')
                negative_score = 0

                for must_have in hmust_haves:
                    if hood[must_have] != 1:
                        negative_score += 20

            else :

                passed_musthaves = False

            for must_have in umust_haves:
                if listing.has_key(must_have):
                    if listing[must_have] != 1 and must_have not in ["sublet_roomate", "studio"]:
                        negative_score += 20


            passed_musthaves = True
            if ldatetime >= idatetime:
                passed_musthaves = False

            if 0 not in bed_range:
                if listing["studio"] == 1:
                    passed_musthaves = False


            if passed_musthaves:
                listing["score"] = 0
                for key in listing.keys():
                    if key in udelighters:
                        if listing[key] == 1:
                            listing["score"] += 30
                    elif listing[key] == 1 and key in ['laundry', 'hardwood', 'lighting', 'kitchen', 'deck_balcony', 'ameneties', 'cieling'] :
                        listing["score"] +=10
                for key in hood.keys():
                    if key in hdelighters:
                        if hood[key] == 1:
                            listing["score"] += 30
                    elif hood[key] == 1 and key in ['Safe', 'Locales_good', 'Parks']:
                        listing["score"] += 10


                price = float(information["budget"] - listing["price"]) / float(information["budget"])
                price_list.append(listing["price"])
                price_score = price * 100.00
                listing["score"] += int(price_score)
                listing["score"] = listing["score"] - negative_score
                score_list.append(listing["score"])
                listing["relevance"] = (float(listing["score"]) * 20.00) / 200.00
                if listing["relevance"] > 20:
                    listing["relevance"] = 20
                final_filter.append(listing)

        sorted_list = sorted(final_filter, key=itemgetter('score'), reverse=True)

        final_list = []
        if len(score_list) >0:
            arr_score = numpy.array([score_list])
            mean_score =  int(numpy.mean(arr_score))
            standard_dev_score =  int(numpy.std(arr_score))
            lower_score = mean_score-(standard_dev_score*2)
            upper_score = mean_score+(standard_dev_score*2)

            arr_price = numpy.array([price_list])
            mean_price =  int(numpy.mean(arr_price))
            standard_dev_price =  int(numpy.std(arr_price))
            lower_price = mean_price-(int(standard_dev_price*1))
            upper_price = mean_price+(int(standard_dev_price*2))

            for element in sorted_list:
                if element["score"] in range(lower_score, upper_score) and element["price"] in range(lower_price, upper_price):
                    final_list.append(element)
        else:
            final_list = sorted_list

        complete_length = len(final_list)
        if skipNumber < complete_length:
            final_list = final_list[limitNumber:skipNumber]
        else:
            final_list = final_list[limitNumber:]


        pages = int(math.ceil(float(complete_length) / float(requestItems)))

        user_email = ""
        if "email" in information.keys():
            user_email = information["email"]

        # returns the list of data objects

        reponseObj.Data = ListingList(4,jsonpickle.decode(dumps(final_list)),complete_length, user_email, pages)
        BaseUtils.SetOKDTO(reponseObj)



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