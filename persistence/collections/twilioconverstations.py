
from bson.objectid import ObjectId

class TwilioConvertations():

    def __init__(self, db):
        self.__collectionName__ = "twilioconversations"
        self.__db__ = db
        self.__loadConnection()

    def __loadConnection(self):
        self.__collectionObject__ = self.__db__[self.__collectionName__]

    def get_conversation_by_user_and_listing_owner_ids(self, user_id, listing_owner_id):
        conversation_object = self.__collectionObject__.find_one({'user_id': user_id, 'listing_owner_id': listing_owner_id, 'status': 'active'})
        return conversation_object

     # return user
    def get_conversation_by_phone(self, twilio_number, listing_owner_number):
        print "twilio_number"
        print twilio_number
        print 'listing_owner_number'
        print listing_owner_number
        conversation_object = self.__collectionObject__.find_one({'twilio_number': twilio_number, 'status': "active", 'listing_owner_number': listing_owner_number})
        print "conversation_object"
        print conversation_object
        return conversation_object

    def add_conversation(self, twilio_number, listing_owner_number, user_id, listing_owner_id):
        # sample data
        return self.__collectionObject__.insert({'twilio_number': twilio_number, 'listing_owner_number': listing_owner_number, 'status': 'active' ,'user_id': user_id, 'listing_owner_id': listing_owner_id})

    def add_test_data(self):
        # sample data
        message1 = {'from_number': '+573202524157', 'to_number': '+16179345762', 'status': 'active'}
        self.__collectionObject__.insert(message1)