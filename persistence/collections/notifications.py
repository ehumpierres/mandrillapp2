
from bson.objectid import ObjectId

class Notifications():

    def __init__(self, db):
        self.__collectionName__ = "notifications"
        self.__db__ = db
        self.__loadConnection()

    def __loadConnection(self):
        self.__collectionObject__ = self.__db__[self.__collectionName__]

    # return messages
    def get_unread_notifications(self, user_id):
        filter_object = {'user_id': ObjectId(user_id), 'read': False}
        fields_object = {'content': 1, '_id': 0}
        notification_cursor = self.__collectionObject__.find(filter_object, fields_object)
        notification_list = list(notification_cursor)
        notification_list_len = len(notification_list)
        if notification_list_len > 0:
            return {'count':notification_list_len, 'notifications': notification_list}
        else:
            return {'count': 0, 'notifications': []}

    def add_test_data(self):
        message1 = {'user_id': ObjectId('5349b4ddd2781d08c09890a1'), 'content': 'you have a new message', 'read': True}
        message2 = {'user_id': ObjectId('5349b4ddd2781d08c09890a1'), 'content': 'you have a new message', 'read': False}
        message3 = {'user_id': ObjectId('5349b4ddd2781d08c09890a1'), 'content': 'you have been accepted to start the rental process!!', 'read': False}
        self.__collectionObject__.insert(message1)
        self.__collectionObject__.insert(message2)
        self.__collectionObject__.insert(message3)