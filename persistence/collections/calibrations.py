from bson.objectid import ObjectId

class Calibrations():

    def __init__(self, db):
        self.__collectionName__ = "calibrations"
        self.__db__ = db
        self.__loadConnection()

    def __loadConnection(self):
        self.__collectionObject__ = self.__db__[self.__collectionName__]

    # return calibration value
    def get_calibration_value(self, city, bedrooms, budget):
        filter_object = {'city': city, 'bedrooms': bedrooms, 'max_budget': {'$gte': budget}, 'min_budget': {'$lte': budget}}
        fields_object = {'calibration_value': 1, '_id': 0}
        calibration_cursor = self.__collectionObject__.find(filter_object, fields_object)
        print calibration_cursor
        calibration_list = list(calibration_cursor)
        if len(calibration_list)>0:
            calibration_element = calibration_list[0]
            return calibration_element['calibration_value']
        else:
            return None
        return calibration_element

    def add_test_data(self):
        # calibrations
        calibration_value_1 = {'_id': ObjectId('5349b4ddd2781d08c09890c1'), 'city': 'New York City', 'min_budget': 0, 'max_budget': 500, 'bedrooms': 1, 'calibration_value': 0}
        calibration_value_2 = {'_id': ObjectId('5349b4ddd2781d08c09890c2'), 'city': 'New York City', 'min_budget': 500, 'max_budget': 1000, 'bedrooms': 1, 'calibration_value': 20}
        calibration_value_3 = {'_id': ObjectId('5349b4ddd2781d08c09890c3'), 'city': 'New York City', 'min_budget': 1000, 'max_budget': 1500, 'bedrooms': 1, 'calibration_value': 50}
        calibration_value_4 = {'_id': ObjectId('5349b4ddd2781d08c0989043'), 'city': 'New York City', 'min_budget': 1500, 'max_budget': 2000, 'bedrooms': 1, 'calibration_value': 70}
        self.__collectionObject__.insert(calibration_value_1)
        self.__collectionObject__.insert(calibration_value_2)
        self.__collectionObject__.insert(calibration_value_3)
        self.__collectionObject__.insert(calibration_value_4)
