
from bson.objectid import ObjectId

class TwilioNumbers():

    def __init__(self, db):
        self.__collectionName__ = "twilionumbers"
        self.__db__ = db
        self.__loadConnection()

    def __loadConnection(self):
        self.__collectionObject__ = self.__db__[self.__collectionName__]

    def get_random_available_number_and_mark_as_unavailable(self):
        twilio_number_obj = self.__collectionObject__.find_one({'status': 'available'})
        print "twilio_number_obj"
        print twilio_number_obj
        if twilio_number_obj is not None:
            twilio_number_obj['status'] = 'busy'
            twilio_number = twilio_number_obj['number']
            print "twilio_number"
            print twilio_number
            self.__collectionObject__.update({'_id': twilio_number_obj['_id']}, twilio_number_obj, True)
        return twilio_number

    def add_test_data(self):
        # sample data
        message1 = {'number': '+16179345762', 'status': 'available'}
        self.__collectionObject__.insert(message1)