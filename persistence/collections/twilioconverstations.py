
from bson.objectid import ObjectId

class TwilioConvertations():

    def __init__(self, db):
        self.__collectionName__ = "twilioconversations"
        self.__db__ = db
        self.__loadConnection()

    def __loadConnection(self):
        self.__collectionObject__ = self.__db__[self.__collectionName__]

    def add_conversation(self, from_number, to_number):
        # sample data
        return self.__collectionObject__.insert({'from_number': from_number, 'to_number': to_number, 'status': 'active'})

    def add_test_data(self):
        # sample data
        message1 = {'from_number': '+573202524157', 'to_number': '+16179345762', 'status': 'active'}
        self.__collectionObject__.insert(message1)