
from bson.objectid import ObjectId

class Messages():

    def __init__(self, db):
        self.__collectionName__ = "messages"
        self.__db__ = db
        self.__loadConnection()

    def __loadConnection(self):
        self.__collectionObject__ = self.__db__[self.__collectionName__]

    # TODO: save this data in a normalized way using listing owner ids instead the phone number
    # save message
    def save_message(self, from_type, listing_owner_phone_number, user_id, content, is_broadcast, sid, twilio_conversation_id):
        insert_object = {'fromType': from_type, 'listing_owner_phone_number': listing_owner_phone_number , 'user_id':user_id, 'content': content, 'is_broadcast': is_broadcast, 'twilio_sid': sid , 'twilio_conversation_id':twilio_conversation_id}
        self.__collectionObject__.insert(insert_object)

    def save_messages(self, from_type, listing_owner_phone_number_list, user_id, content, is_broadcast):
        for listing_owner_phone_number in listing_owner_phone_number_list:
            self.save_message(from_type, listing_owner_phone_number, user_id, content, is_broadcast)

    # return messages
    def get_received_messages(self, user_id):
        print "user_id"
        print user_id
        filter_object = {'fromType': 'listing_owner', 'user_id': ObjectId(user_id)}
        fields_object = {'content': 1, '_id': 0}
        message_cursor = self.__collectionObject__.find(filter_object, fields_object)
        message_list = list(message_cursor)
        if len(message_list) > 0:
            return message_list
        else:
            return []

    def add_test_data(self):
        # from user to listing owners
        message1 = {'fromType': 'user', 'user_id': ObjectId('5349b4ddd2781d08c09890a1'), 'listing_owner_id':ObjectId('5349b4ddd2781d08c09890f1'), 'content': 'Looking for an apartment'}
        message2 = {'fromType': 'user', 'user_id': ObjectId('5349b4ddd2781d08c09890a1'), 'listing_owner_id':ObjectId('5349b4ddd2781d08c09890f2'), 'content': 'Looking for an apartment'}
        message3 = {'fromType': 'user', 'user_id': ObjectId('5349b4ddd2781d08c09890a1'), 'listing_owner_id':ObjectId('5349b4ddd2781d08c09890f3'), 'content': 'Looking for an apartment'}
        message4 = {'fromType': 'listing_owner', 'user_id': ObjectId('5349b4ddd2781d08c09890a1'), 'listing_owner_id':ObjectId('5349b4ddd2781d08c09890f3'), 'content': 'I have the perfect apartment for you'}
        self.__collectionObject__.insert(message1)
        self.__collectionObject__.insert(message2)
        self.__collectionObject__.insert(message3)
        self.__collectionObject__.insert(message4)