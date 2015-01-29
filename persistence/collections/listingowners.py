
class ListingOwners():

    def __init__(self, db):
        self.__collectionName__ = "listing_owners"
        self.__db__ = db
        self.__loadConnection()

    def __loadConnection(self):
        self.__collectionObject__ = self.__db__[self.__collectionName__]

    # returns listings owners list
    def gell_all_listing_owners(self):
        listing_owners_cursors = self.__collectionObject__.find()
        listing_owners_list = list(listing_owners_cursors)
        return listing_owners_list
