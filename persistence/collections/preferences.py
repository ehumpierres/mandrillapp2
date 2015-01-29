
class Preferences():

    def __init__(self, db):
        self.__collectionName__ = "user_preferences"
        self.__db__ = db
        self.__loadConnection()

    def __loadConnection(self):
        self.__collectionObject__ = self.__db__[self.__collectionName__]

    def save_preference(self, preference_obj):
        self.__collectionObject__.insert(preference_obj)
