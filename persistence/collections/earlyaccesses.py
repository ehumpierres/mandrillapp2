
class EarlyAccesses():

    def __init__(self, db):
        self.__collectionName__ = "earlyaccesses"
        self.__db__ = db
        self.__loadConnection()

    def __loadConnection(self):
        self.__collectionObject__ = self.__db__[self.__collectionName__]

    def save_early_access(self, early_access_obj):
        self.__collectionObject__.insert(early_access_obj)
