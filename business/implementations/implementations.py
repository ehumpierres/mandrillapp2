from persistence.mongodatabase import mongoDatabase
from pymongo import MongoClient

from business.utils.mailsender import MailSender

from business.implementations.pointcalculator import PointCalculator

from persistence.collections.listings import Listings
from persistence.collections.listingoptions import ListingOptions
from persistence.collections.neighborhoods import Neighborhoods


class Implementations():
    def __init__(self):

        # load constants
        # self.__MONGO_URL__ = "mongodb://jhon:1234@kahana.mongohq.com:10066/app30172457"
        #self.__MONGO_DB__ = "app30172457"

        self.__MONGO_URL__ = "mongodb://jhon:jhon@dogen.mongohq.com:10021/app31380057"
        self.__MONGO_DB__ = "app31380057"


        # init db connection
        self.__myDB__ = mongoDatabase(self.__MONGO_URL__)
        self.__db__ = self.__myDB__.getDB(self.__MONGO_DB__)

    def update_neighborhood_info(self, listing_id=None, neighborhoods_coords=None):
        return_success = False

        if listing_id is not None and neighborhoods_coords is not None:
            listing_collection_persistence = Listings(self.__db__)
            neighborhood_collection_persistence = Neighborhoods(self.__db__)
            # get single listing coords
            listings_coords = listing_collection_persistence.get_unit_listing_coords_by_listing_id(listing_id)
            # implement class that has ANN algorithms
            print "listings_coords", listings_coords
            print "neighborhoods_coords", neighborhoods_coords
            new_point_calculator = PointCalculator(neighborhoods_coords, listings_coords)
            # get coords of all the neighbors
            array_coords = new_point_calculator.get_nearest_point_array_coords()
            # get neighbor based on its coords
            nearest_neighborhood = neighborhood_collection_persistence.get_neighborhood_by_coords(array_coords[0],
                                                                                                  array_coords[1])
            # uddate listing neighborId
            listing_collection_persistence.update_listing_neighborhood_by_listing_id(listing_id, nearest_neighborhood)
            return_success = True

        return return_success

    def save_listing(self, listing_dic):
        listing_collection = Listings(self.__db__)
        return_listing_id = listing_collection.insert_listing(listing_dic)
        return return_listing_id

    def sendEmailToContact(self, listingid=None, useremail=None):
        returnSuccess = False

        if listingid is not None and useremail is not None:
            listingCollection = Listings(self.__db__)
            # get landlord email
            landLordEmail = listingCollection.getLandLordEmailByListingId(listingid)
            # # instantiate email sender object
            mailSenderObj = MailSender('smtp.gmail.com', 587, 'jhon@socrex.com', '123456789@Socrex')
            ## send email
            mailSenderObj.sendEmail(useremail, landLordEmail, 'subject test', 'subject body')
            ## email quit sender object
            mailSenderObj.quit()

            # save hit in the listing option collection
            listingOptionCollection = ListingOptions(self.__db__)
            listingOptionCollection.saveListingOptionClick(listingid, useremail, "contact")

            ## add ok code to dto
            returnSuccess = True

        return returnSuccess

    def sendEmailConcierge(self, email, username, userphone, listing_url, listingid):
        returnSuccess = False

        if email is not None and username is not None and userphone is not None and listing_url is not None and listingid is not None:
            listingCollection = Listings(self.__db__)

            subject = str(username) + " - " + str(listingid)
            body = "User: " + username + "<br> Email: " + email + "<br> Phone: " + userphone + "<br> Url: <a href=\"" + listing_url + "\">" + listing_url + "</a>"
            # get landlord email
            # # instantiate email sender object
            mailSenderObj = MailSender('smtp.gmail.com', 587, 'concierge@socrex.com', 'monaco123')
            ## send email
            mailSenderObj.sendEmail('concierge@socrex.com', 'concierge@socrex.com', subject, body)
            ## email quit sender object
            mailSenderObj.quit()

            # save hit in the listing option collection
            # listingOptionCollection = ListingOptions(self.__db__)
            # listingOptionCollection.saveListingOptionClick(listingid,useremail,"contact")

            ## add ok code to dto
            returnSuccess = True

        return returnSuccess

    def verifyListingAvailability(self, listingid=None, useremail=None):
        returnSuccess = False

        if listingid is not None and useremail is not None:
            # save hit in the listing option collection
            listingOptionCollection = ListingOptions(self.__db__)
            listingOptionCollection.saveListingOptionClick(listingid, useremail, "verifyavailability")

            returnSuccess = True

        return returnSuccess

    def expertReview(self, listingid=None, useremail=None):
        returnSuccess = False

        if listingid is not None and useremail is not None:
            # save hit in the listing option collection
            listingOptionCollection = ListingOptions(self.__db__)
            listingOptionCollection.saveListingOptionClick(listingid, useremail, "expertreview")

            returnSuccess = True

        return returnSuccess

    def virtualTour(self, listingid=None, useremail=None):
        returnSuccess = False

        if listingid is not None and useremail is not None:
            # save hit in the listing option collection
            listingOptionCollection = ListingOptions(self.__db__)
            listingOptionCollection.saveListingOptionClick(listingid, useremail, "virtualtour")

            returnSuccess = True

        return returnSuccess

    def listingDetails(self, listingid=None):
        returnSuccess = False

        if listingid is not None:
            # save hit in the listing option collection
            listingOptionCollection = ListingOptions(self.__db__)
            # listingOptionCollection.saveListingOptionClick(listingid,useremail,"listingdetails")

            returnSuccess = True

        return returnSuccess

    def originalListing(self, listingid=None, useremail=None):
        returnSuccess = False

        if listingid is not None and useremail is not None:
            # save hit in the listing option collection
            listingOptionCollection = ListingOptions(self.__db__)
            listingOptionCollection.saveListingOptionClick(listingid, useremail, "originallisting")

            returnSuccess = True

        return returnSuccess
        
        