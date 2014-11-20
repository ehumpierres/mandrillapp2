
class Neighborhoods():

    def __init__(self, db):
        self.__collectionName__ = "hoods"
        self.__db__ = db
        self.__loadConnection()

    def __loadConnection(self):
        self.__collectionObject__ = self.__db__[self.__collectionName__]

    def get_neighborhoods_coordinates(self):
        return_neighborhoods_coords = None
        neighborhood_objs = self.__collectionObject__.find()
        if neighborhood_objs:
            return_neighborhoods_coords = []
            for neighborhood_obj in neighborhood_objs:
                for coordinate in neighborhood_obj["Coordinates"]:
                    return_neighborhoods_coords.append([coordinate['Latitude'], coordinate['Longitude']])
        return return_neighborhoods_coords

    def get_neighborhood_by_coords(self, latitude, longitude):
        returnObj = None
        if latitude is not None and longitude  is not None :
            # modify based on he new structure
            #shapes: {$elemMatch: {color: "red"}}
            # $in: [latitude, longitude]
            print "latitude" , latitude
            print "longitude" , longitude
            neighborhoodObj = self.__collectionObject__.find_one({ 'Coordinates': { '$elemMatch': {"Latitude": latitude , "Longitude": longitude}} } )
            print "neighborhoodObj" , neighborhoodObj
            if neighborhoodObj:
                returnObj = neighborhoodObj
                #returnObj = {"_id":neighborhoodObj["_id"] , "Name":neighborhoodObj["Name"]}
        return returnObj
