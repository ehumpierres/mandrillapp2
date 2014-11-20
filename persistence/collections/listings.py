
# mongodb
from pymongo import MongoClient
from bson.objectid import ObjectId

class Listings():
    
    def __init__(self, db):
        self.__collectionName__ = "listingoptions"
        self.__db__ = db
        self.__loadConnection()
    
    def __loadConnection(self):
        self.__collectionObject__ = self.__db__[self.__collectionName__]

    def insert_listing(self, listing_dic):
        return_listing_id = self.__collectionObject__.insert(listing_dic)
        return return_listing_id

    def get_unit_listing_coords_by_listing_id(self, listing_id):
        return_coord = None
        if listing_id is not None:
            listing_obj = self.__collectionObject__.find_one({'_id': ObjectId(listing_id)} )
            if listing_obj:
                ## from string to float
                return_coord = [float(listing_obj["latitude"]), float(listing_obj["longitude"])]
        return return_coord
        
    def update_listing_neighborhood_by_listing_id(self, listing_id, neighborhood_obj):
        return_value = False
        if listing_id is not None:
            listing_obj = self.__collectionObject__.update({'_id': ObjectId(listing_id)},{"$set":{'neighborhood':neighborhood_obj}} )
            return_value = True
        return return_value
        

    def getLandLordEmailByListingId(self , listingid):
        landlordEmail = ""
        # missing email field in the database: the crawler must pull that info
        #landlordEmail = self.__collectionObject__.find_one({'_id': ObjectId(listingid)} )
        landlordEmail = "jhonjairoroa87@gmail.com"
        return landlordEmail