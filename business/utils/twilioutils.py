import mandrill
import datetime
import ConfigParser
from twilio.rest import TwilioRestClient

class TwilioUtils():

    def __init__(self):
        self.__load_config_info__()
        self.__load_twilio_client__()

    def __load_config_info__(self):
        config = ConfigParser.ConfigParser()
        config.read("config.cfg")
        twilio_section = 'twilio_config'
        ## load config keys
        self.__account_sid__ = config.get(twilio_section, 'account_sid')
        self.__auth_token__ = config.get(twilio_section, 'auth_token')

    def __load_twilio_client__(self):
        self.__client__ = TwilioRestClient(self.__account_sid__, self.__auth_token__)


    def send_broadcast_to_listing_owners(self, from_number, message, phone_numbers_list):
        for phone_number in phone_numbers_list:
            self.send_message_to_number(from_number, message, phone_number)

    def search_and_buy_number(self):
        numbers = self.__client__.phone_numbers.search()
        if numbers:
            number = numbers[0]
            number.purchase()
            print "number"
            print number
            return number
        else:
            print "there were no numbers available to buy"
            return None

    def send_message_to_number(self, message, from_number , to_number):
        try:
            #sends the sms using the twilio client
            self.__client__.messages.create(body=message, to=to_number, from_=from_number)
            return "success"
        #except twilio.TwilioRestException as e:
        except Exception as e:
            print "error sending message via twilio"
            print e
            return "failed"




