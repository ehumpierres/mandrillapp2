from bson.objectid import ObjectId

class ListingOwners():

    def __init__(self, db):
        self.__collectionName__ = "listing_owners"
        self.__db__ = db
        self.__loadConnection()

    def __loadConnection(self):
        self.__collectionObject__ = self.__db__[self.__collectionName__]


    # TODO: complete this method when needed
    # returns listings owners id list given a listings owners phone number list
    def gell_listing_owner_ids_by_phone_numbers(self, listing_owners_phone_number_list):
        listing_owners_phone_numbers_cursors = self.__collectionObject__.find({}, {'phone': 1, '_id': 0})
        listing_owners_phone_numbers_list = list(listing_owners_phone_numbers_cursors)
        final_phone_list = [x['phone'] for x in listing_owners_phone_numbers_list if 'phone' in x]
        return final_phone_list

    # returns listings owners numbers list
    def gell_all_listing_owners_phone_numbers(self):
        listing_owners_phone_numbers_cursors = self.__collectionObject__.find({}, {'phone': 1, '_id': 0})
        listing_owners_phone_numbers_list = list(listing_owners_phone_numbers_cursors)
        final_phone_list = [x['phone'] for x in listing_owners_phone_numbers_list if 'phone' in x]
        return final_phone_list

    # returns listings owners list
    def gell_all_listing_owners(self):
        listing_owners_phone_numbers_cursors = self.__collectionObject__.find({}, {'phone': 1, '_id': 1})
        listing_owners_phone_numbers_list = list(listing_owners_phone_numbers_cursors)
        return listing_owners_phone_numbers_list

    # returns a particular listing owner
    def gell_listing_owner(self, listing_owner_id):
        filter_object = {'_id': ObjectId(listing_owner_id)}
        fields_object = {'_id': 0}
        listing_owners_cursors = self.__collectionObject__.find(filter_object,fields_object)
        listing_owners_list = list(listing_owners_cursors)
        print "listing_owners_list"
        print listing_owners_list
        return listing_owners_list

    def add_test_data(self):
        # from user to listing owners
        listing_owner_1 = {'_id': ObjectId('5349b4ddd2781d08c09890f1'), 'fullname': 'Gerald K. Ramey'   , 'email': 'GeraldKRamey@rhyta.com'     , 'phone': '717-892-5401'}
        listing_owner_2 = {'_id': ObjectId('5349b4ddd2781d08c09890f2'), 'fullname': 'Sarah J. Sanderson', 'email': 'SarahJSanderson@teleworm.us', 'phone': '850-267-6795'}
        listing_owner_3 = {'_id': ObjectId('5349b4ddd2781d08c09890f3'), 'fullname': 'Denise J. Mitchell', 'email': 'DeniseJMitchell@teleworm.us', 'phone': '218-728-9878'}
        self.__collectionObject__.insert(listing_owner_1)
        self.__collectionObject__.insert(listing_owner_2)
        self.__collectionObject__.insert(listing_owner_3)

