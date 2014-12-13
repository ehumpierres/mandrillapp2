# flask imports
from flask import Flask
from flask import request
from flask import Response

# Import smtplib for the actual sending function
# import smtplib
# from email.MIMEMultipart import MIMEMultipart
# from email.MIMEText import MIMEText
# from business.utils.mailsender import MailSender

#load api services
#user actions
from services.useractions.addshortlist import add_shortlist_api
from services.useractions.addapplylist import add_applylist_api
from services.useractions.addshortlistbulk import add_bulk_shortlist_api
from services.useractions.deleteshortlist import delete_shortlist_api
from services.useractions.getshortlist import get_shortlist_api
from services.useractions.emailconcierge import concierge_email_api
from services.useractions.addusercomment import add_user_comment_api
from services.useractions.createuser import create_user_api


#trotter actions
from services.trotteractions.recommend import recommend_api
from services.trotteractions.changestatus import change_status_api
from services.trotteractions.addlisting import add_listing_api
from services.trotteractions.addvideolink import add_video_link_api
from services.trotteractions.adddocumentlink import add_document_link_api
from services.trotteractions.addtrottercomment import add_trotter_comment_api
from services.trotteractions.addlisting import add_listing_api


#listing actions
from services.listings.filterlistings import filter_listings_api
from services.listings.getlisting import get_listing_api
from services.listings.getcomments import get_comments_api
from services.listings.getlistingsdetails import get_listing_details_api

#preferences actions
from services.preferences.savepreferences import save_preferences_api
from services.preferences.getpreferences import get_preferences_api

# init flask app
app = Flask(__name__)

# add blueprint services

app.register_blueprint(add_shortlist_api)
app.register_blueprint(add_applylist_api)
app.register_blueprint(add_bulk_shortlist_api)
app.register_blueprint(delete_shortlist_api)
app.register_blueprint(get_shortlist_api)
app.register_blueprint(recommend_api)
app.register_blueprint(change_status_api)
app.register_blueprint(filter_listings_api)
app.register_blueprint(get_listing_api)
app.register_blueprint(save_preferences_api)
app.register_blueprint(get_preferences_api)
app.register_blueprint(concierge_email_api)
app.register_blueprint(add_video_link_api)
app.register_blueprint(add_document_link_api)
app.register_blueprint(add_listing_api)
app.register_blueprint(add_trotter_comment_api)
app.register_blueprint(add_user_comment_api)
app.register_blueprint(get_comments_api)
app.register_blueprint(get_listing_details_api)
app.register_blueprint(create_user_api)


@app.route('/')
def deploy_success():
    return 'This application has deployed successfully.'


# @app.route('/listing/<listingid>/user/<useremail>/sendemail', methods = ['POST'])
# def sendEmailToContact(listingid= None, useremail=None ):

#     reponseObj = Base()

#     try:
#         isSuccessful = newImplementation.sendEmailToContact(listingid, useremail)
#         if isSuccessful:
#             BaseUtils.SetOKDTO(reponseObj)
#         else:
#             ## todo: implement code for not nullable listingid or  useremail
#             BaseUtils.SetUnexpectedErrorDTO(reponseObj)
#     # TODO: IMPLEMENT APROPIATE ERROR HANDLING
#     except Exception as e:
#         BaseUtils.SetUnexpectedErrorDTO(reponseObj)
#         print "There was an unexpected error: " , str(e)
#         print traceback.format_exc()

#     jsonObj = jsonpickle.encode(reponseObj, unpicklable=False)
#     response = Response(jsonObj)
#     response.headers.add('Access-Control-Allow-Origin', '*')
#     response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS, GET')
#     return response



if __name__ == '__main__':
    app.debug = True
    # enable to run in cloud9
    # hostip = os.environ['IP']
    hostip = "0.0.0.0"
    # hostport = int(os.environ['PORT'])
    hostport = int(8080)
    # hostip = os.getenv('IP', '0.0.0.0')
    # hostport = os.getenv('PORT', 8080)
    # print "type(hostport)" , type(hostport)
    app.run(host=hostip,port=hostport)
    # enable to run in heroku
    # app.run()
