

from bson.objectid import ObjectId

class MongoUtils():

    def __init__(self):
        pass

    # Transform a list of string to a list of objects id
    @staticmethod
    def to_object_id(string_id_list):
        return_list = []
        for string_id in string_id_list:
            return_list.append(ObjectId(string_id))
        return return_list
