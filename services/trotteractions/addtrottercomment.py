# flask imports
from flask import Flask
from flask import request
from flask import Response
from flask import Blueprint

import traceback
import time
from datetime import date

# json handling
import jsonpickle
from bson.json_util import dumps
from bson.objectid import ObjectId

from dto.response.classes.base import Base
from dto.response.utils.baseutils import BaseUtils

from persistence.mongodatabase import mongoDatabase


# load constants
MONGO_URL = 'mongodb://jhon:1234@dogen.mongohq.com:10080/app31803464'
MONGO_DB = "app31803464"
# MONGO_URL = "mongodb://jhon:1234@kahana.mongohq.com:10066/app30172457"
# MONGO_DB = "app30172457"

# init db connection
myDB = mongoDatabase(MONGO_URL)
db = myDB.getDB(MONGO_DB)

add_trotter_comment_api = Blueprint('add_trotter_comment_api', __name__)

@add_trotter_comment_api.route('/addtrottercomment', methods=['POST'])
def add_trotter_comment():
    reponse_obj = Base()
    try:
        request_user = request.form['userid']
        request_trotter = request.form['trotterid']
        request_comment = request.form['comment']

        usersCollection = db['users']
        trottersCollection = db['trotters']

        user = usersCollection.find_one({"_id" : ObjectId(request_user)})
        trotter = trottersCollection.find_one({"_id" : ObjectId(request_trotter)})

        comments = user['comments']
        comment = dict()
        comment['commenter'] = trotter['fullname']
        comment_date = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        comment['timestamp'] = time.time()
        comment['date'] = comment_date
        comment['text'] = request_comment
        comment['type'] = 'trotter'
        comments.append(comment)

        # for entry in shortlist:
        #     if entry['_id'] == ObjectId(request_listing):
        #         if 'comments' not in entry.keys():
        #             entry['comments'] = []
        #         entry['comments'].append(comment)
        #         result_bool = True

        usersCollection.update({'_id':user['_id']}, {'$set':{'comments':comments}})

        reponse_obj.Data = jsonpickle.decode(dumps({'result': True}))
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
