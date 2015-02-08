from bson.objectid import ObjectId

class Preferences():

    def __init__(self, db):
        self.__collectionName__ = "user_preferences"
        self.__db__ = db
        self.__loadConnection()

    def __loadConnection(self):
        self.__collectionObject__ = self.__db__[self.__collectionName__]

    def save_preference(self, preference_obj):
        self.__collectionObject__.insert(preference_obj)

    def add_test_data(self):
        # from user to listing owners
        preference_1 = {'_id': ObjectId('5349b4ddd2781d08c09890b1'), 'user_id': ObjectId('5349b4ddd2781d08c09890a1'), 'city': 'New York City', 'bedrooms': 3, 'budget': 2000}
        preference_2 = {'_id': ObjectId('5349b4ddd2781d08c09890b2'), 'user_id': ObjectId('5349b4ddd2781d08c09890a2'), 'city': 'New York City', 'bedrooms': 2, 'budget': 2500}
        preference_3 = {'_id': ObjectId('5349b4ddd2781d08c09890b3'), 'user_id': ObjectId('5349b4ddd2781d08c09890a3'), 'city': 'New York City', 'bedrooms': 1, 'budget': 1000}
        self.__collectionObject__.insert(preference_1)
        self.__collectionObject__.insert(preference_2)
        self.__collectionObject__.insert(preference_3)
