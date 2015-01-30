from bson.objectid import ObjectId

class Users():

    def __init__(self, db):
        self.__collectionName__ = "users"
        self.__db__ = db
        self.__loadConnection()

    def __loadConnection(self):
        self.__collectionObject__ = self.__db__[self.__collectionName__]

    # return user_id
    def save_user(self, user_obj):
        return self.__collectionObject__.insert(user_obj)

    def add_test_data(self):
        # from user to listing owners
        listing_owner_1 = {'_id': ObjectId('5349b4ddd2781d08c09890a1'), 'fullname': 'jhon jairo roa'   , 'email': 'jhon@gotrotter.com'     , 'phone': '717-892-5402'}
        listing_owner_2 = {'_id': ObjectId('5349b4ddd2781d08c09890a2'), 'fullname': 'ernesto humpierres', 'email': 'ernesto@gotrotter.com', 'phone': '850-267-6796'}
        listing_owner_3 = {'_id': ObjectId('5349b4ddd2781d08c09890a3'), 'fullname': 'edwin jerez', 'email': 'edwin@gotrotter.com', 'phone': '218-728-9879'}
        self.__collectionObject__.insert(listing_owner_1)
        self.__collectionObject__.insert(listing_owner_2)
        self.__collectionObject__.insert(listing_owner_3)
