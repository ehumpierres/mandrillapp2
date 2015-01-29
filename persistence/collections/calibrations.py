
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
