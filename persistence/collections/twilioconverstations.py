
from bson.objectid import ObjectId

class TwilioConvertations():

    def __init__(self, db):
        self.__collectionName__ = "twilioconversations"
        self.__db__ = db
        self.__loadConnection()

    def __loadConnection(self):
        self.__collectionObject__ = self.__db__[self.__collectionName__]

     # return user
    def get_conversation_by_phone(self, from_number, to_number):
        print "from_number"
        print from_number
        print 'to_number'
        print to_number
        conversation_object = self.__collectionObject__.find_one({'from_number': from_number, 'status': "active", 'to_number': to_number})
        print "conversation_object"
        print conversation_object
        return conversation_object

    def add_conversation(self, from_number, to_number, user_id):
        # sample data
        return self.__collectionObject__.insert({'from_number': from_number, 'to_number': to_number, 'status': 'active' , 'user_id': user_id})

    def add_test_data(self):
        # sample data
        message1 = {'from_number': '+573202524157', 'to_number': '+16179345762', 'status': 'active'}
        self.__collectionObject__.insert(message1)