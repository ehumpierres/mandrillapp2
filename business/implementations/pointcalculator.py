
import numpy

from nearpy import Engine
from nearpy.hashes import RandomBinaryProjections

class PointCalculator():

    def __init__(self, point_list, point):
        self.__configure_calculator(point_list, point)

    def __configure_calculator(self, point_list, point ):
        # Dimension of our vector space
        self.__dimension__ = 2

        # Create a random binary hash with 10 bits
        self.__rbp__ = RandomBinaryProjections('rbp', 10)

        # Create engine with pipeline configuration
        self.__engine__ = Engine(self.__dimension__, lshashes=[self.__rbp__])
        self.setSearchingPointList(point_list)
        self.setQueryPoint(point)

    def __load_point_list_in_engine(self):
        for index in xrange(0,len(self.__pointList__)):
            v = numpy.array(self.__pointList__[index])
            self.__engine__.store_vector(v, 'data_%d' % index)

    def set_searching_point_list(self, point_list):
        self.__point_list__ = point_list
        self.__load_point_list_in_engine()

    def set_query_point(self, point):
        self.__point__ = point

    def __get_nearest_point(self):
        return self.__engine__.neighbours(numpy.array(self.__point__))

    def get_nearest_point_array_coords(self):
        nearest_point = self.__get_nearest_point()
        return [nearest_point[0][0][0],nearest_point[0][0][1]]


