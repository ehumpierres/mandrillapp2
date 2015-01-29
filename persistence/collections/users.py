
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
