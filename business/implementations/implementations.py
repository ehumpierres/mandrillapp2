import ConfigParser

from persistence.mongodatabase import mongoDatabase
from pymongo import MongoClient

# utils
from business.utils.mailsender import MailSender
from business.utils.twilioutils import TwilioUtils
from business.utils.mandrillutils import MandrillUtils

from business.implementations.pointcalculator import PointCalculator

# persistence collections
from persistence.collections.listings import Listings
from persistence.collections.listingoptions import ListingOptions
from persistence.collections.neighborhoods import Neighborhoods
from persistence.collections.notifications import Notifications
from persistence.collections.listingowners import ListingOwners
from persistence.collections.messages import Messages
from persistence.collections.users import Users
from persistence.collections.preferences import Preferences
from persistence.collections.calibrations import Calibrations
from persistence.collections.twilionumbers import TwilioNumbers
from persistence.collections.twilioconverstations import TwilioConvertations




class Implementations():
    def __init__(self):

        # TODO: improve the way this vars are loaded
        # load constants
        config = ConfigParser.ConfigParser()
        config.read("config.cfg")
        mongo_section = 'mongo_config'

        # load constants
        self.__MONGO_URL__ = config.get(mongo_section, 'url')
        self.__MONGO_DB__ = config.get(mongo_section, 'db')

        # init db connection
        self.__myDB__ = mongoDatabase(self.__MONGO_URL__)
        self.__db__ = self.__myDB__.getDB(self.__MONGO_DB__)

    def save_preferences(self, fullname, email, phone, budget, bedrooms, city):

        # build user object to be stored in the database
        user_object = {'fullname': fullname, 'email': email, 'phone': phone}

        ## save user in the database
        user_collection_obj = Users(self.__db__)
        user_id = user_collection_obj.save_user(user_object)

        # build preference object to be stored in the database
        preference_object = {'user_id': user_id, 'budget': budget, 'bedrooms': bedrooms, 'city': city}

        ## save preference in the database
        preference_collection_obj = Preferences(self.__db__)
        preference_collection_obj.save_preference(preference_object)

        # TODO: do the broadcast in a different thread asynchronously for improving performance
        # get random free twilio number
        twilio_numbers_instance = TwilioNumbers(self.__db__)
        twilio_number = twilio_numbers_instance.get_random_available_number_and_mark_as_unavailable()
        print "twilio_number"
        print twilio_number

        twilio_utils_instance = TwilioUtils()
        # buy a new number from twilio
        if twilio_number is None:
            twilio_number = twilio_utils_instance.search_and_buy_number()


        # get listing owners from database
        listing_owners_collection_obj = ListingOwners(self.__db__)
        retrieved_listing_owners_phone_numbers = listing_owners_collection_obj.gell_all_listing_owners_phone_numbers()

        print "retrieved_listing_owners_phone_numbers"
        print retrieved_listing_owners_phone_numbers

        for retrieved_listing_owners_phone_number in retrieved_listing_owners_phone_numbers:
            # get random free twilio number
            twilio_conversations_instance = TwilioConvertations(self.__db__)
            twilio_conversation_id = twilio_conversations_instance.add_conversation(twilio_number, retrieved_listing_owners_phone_number, user_id)
            print "twilio_conversation_id"
            print twilio_conversation_id

            # builds message to be sent to the realtors
            message = "I'm looking for an apartment. Budget: " + str(budget) + ", bedrooms: " + str(bedrooms) + ", city: " + city
            # send broadcast using twilio
            twilio_utils_instance.send_message_to_number(message, twilio_number, retrieved_listing_owners_phone_number)

            #save sent message in the db
            messages_collection_obj = Messages(self.__db__)
            messages_collection_obj.save_message('user', retrieved_listing_owners_phone_numbers, user_id, message, True, None, twilio_conversation_id)

        return True

    def save_realtor_twilio_message(self, sid, from_number, to_number, body):

        #save sent message in the db
        messages_collection_obj = Messages(self.__db__)
        messages_collection_obj.save_message('listing_owner', from_number, to_number, body, False, sid, False)

        # get conversation
        conversation_collection_obj = TwilioConvertations(self.__db__)
        conversation_obj = conversation_collection_obj.get_conversation_by_phone(to_number, from_number)

        user_id = conversation_obj['user_id']

        # get info from user
        users_collection_obj = Users(self.__db__)
        users_obj = users_collection_obj.get_user_by_id(user_id)
        user_name = users_obj['fullname']
        user_email = users_obj['email']

        # sent email to user telling that have received a new message from realtor
        mandrill_instance = MandrillUtils()
        # TODO: set the proper url
        mandrill_instance.send_received_message_notification_template_to_user(user_name, user_email, body, "www.google.com")


        return True

    def get_unread_notifications(self, user_id):
        notifications_collection_obj = Notifications(self.__db__)
        return notifications_collection_obj.get_unread_notifications(user_id)

    def load_notifications_test_data(self):
        notifications_collection_obj = Notifications(self.__db__)
        notifications_collection_obj.add_test_data()

    def load_all_database_test_data(self):
        self.load_users_test_data()
        self.load_listing_owners_test_data()
        self.load_messages_test_data()
        self.load_notifications_test_data()

    def load_users_test_data(self):
        users_collection_obj = Users(self.__db__)
        users_collection_obj.add_test_data()

    def load_listing_owners_test_data(self):
         ## get calibration value
        listing_owners_collection_obj = ListingOwners(self.__db__)
        listing_owners_collection_obj.add_test_data()

    def load_messages_test_data(self):
        messages_collection_obj = Messages(self.__db__)
        messages_collection_obj.add_test_data()

    def load_calibrations_test_data(self):
        calibrations_collection_obj = Calibrations(self.__db__)
        calibrations_collection_obj.add_test_data()

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

    def sendEmailConcierge(self, email, username, userphone, listing_url, listingid, request_type):
        returnSuccess = False

        if email is not None and username is not None and userphone is not None and listing_url is not None and listingid is not None and request_type is not None:
            listingCollection = Listings(self.__db__)

            subject = str(username) + " - " + str(listingid)
            body = "User: " + username + "<br> Email: " + email + "<br> Phone: " + userphone + "<br> Url: <a href=\"" + listing_url + "\">" + listing_url + "</a><br>Request: "+request_type
            # get landlord email
            # # instantiate email sender object
            mailSenderObj = MailSender('smtp.gmail.com', 587, 'concierge@gotrotter.com', 'trotterisnumber1')
            ## send email
            mailSenderObj.sendEmail('concierge@gotrotter.com', 'concierge@gotrotter.com', subject, body)
            ## email quit sender object
            mailSenderObj.quit()

            # save hit in the listing option collection
            # listingOptionCollection = ListingOptions(self.__db__)
            # listingOptionCollection.saveListingOptionClick(listingid,useremail,"contact")

            ## add ok code to dto
            returnSuccess = True

        return returnSuccess

    def sendEmailCreateUser(self, name, phone, email, movein, budget, filtersObj):
        returnSuccess = False

        if name is not phone and email is not None and phone is not None and movein is not None and budget is not None and filtersObj is not None:
            listingCollection = Listings(self.__db__)

            subject = "New User: " + str(name)
            body = "User: " + name + "<br> Email: " + email + "<br> Phone: " + phone + "<br> Move-in: " + movein + "<br> Budget: "+budget + "<br> Preferences: "+ filtersObj
            # get landlord email
            # # instantiate email sender object
            mailSenderObj = MailSender('smtp.gmail.com', 587, 'concierge@gotrotter.com', 'trotterisnumber1')
            ## send email
            mailSenderObj.sendEmail('concierge@gotrotter.com', 'concierge@gotrotter.com', subject, body)
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