import mandrill
import datetime
import ConfigParser


class MandrillUtils():

    def __init__(self):
        self.__load_config_info__()
        self.__mandrill_client__ = mandrill.Mandrill(self.__api_key__)

    def __load_config_info__(self):
        config = ConfigParser.ConfigParser()
        config.read("config.cfg")
        mandrill_section = 'mandrill_config'
        self.__api_key__ = config.get(mandrill_section, 'api_key')
        self.__trotter_notification_recipient_email__ = config.get(mandrill_section, 'trotter_notification_recipient_email')
        self.__trotter_notification_recipient_name__ = config.get(mandrill_section, 'trotter_notification_recipient_name')
        self.__user_early_access_template_name__ = config.get(mandrill_section, 'user_early_access_template_name')
        self.__user_early_access_template_subject__ = config.get(mandrill_section, 'user_early_access_template_subject')
        self.__trotter_notification_early_access_template_name__ = config.get(mandrill_section, 'trotter_notification_early_access_template_name')
        self.__trotter_notification_early_access_template_subject__ = config.get(mandrill_section, 'trotter_notification_early_access_template_subject')
        self.__received_message_notification_template_name__ = config.get(mandrill_section, 'received_message_notification_template_name')
        self.__received_message_notification_template_subject__ = config.get(mandrill_section, 'received_message_notification_template_subject')
        print "api key"
        print self.__api_key__

    # send mew message received to user using mandrill template
    def send_received_message_notification_template_to_user(self, user_name, user_email, message_content, message_url):
        template_name = self.__received_message_notification_template_name__
        subject = self.__received_message_notification_template_subject__
        sender_email = 'reply@.inbound.gotrotter.com'
        sender_name = 'Trotter'
        template_user_merge_vars = [
            {"name": "USER_NAME", "content": user_name},
            {"name": "MESSAGE_CONTENT", "content": message_content},
            {"name": "MESSAGE_URL", "content": message_url}
        ]
        self.__send_template__(template_name, sender_email, sender_name, user_email, user_name, subject,  template_user_merge_vars)

    # send early access email to user using mandrill template
    def send_early_access_template_to_user(self, user_name, user_email):
        template_name = self.__user_early_access_template_name__
        subject = self.__user_early_access_template_subject__
        sender_email = 'no-reply@gotrotter.com'
        sender_name = 'Trotter'
        template_user_merge_vars = [
            {"name": "USER_NAME", "content": user_name}
        ]
        self.__send_template__(template_name, sender_email, sender_name, user_email, user_name, subject,  template_user_merge_vars)

    # send early access notification email to trotter using mandrill template
    def send_early_access_notification_template_to_trotter(self, fullname, email, phone):
        template_name = self.__trotter_notification_early_access_template_name__
        recipient_email = self.__trotter_notification_recipient_email__
        recipient_name = self.__trotter_notification_recipient_name__
        subject = self.__trotter_notification_early_access_template_subject__
        sender_email = 'no-reply@gotrotter.com'
        sender_name = 'Trotter'
        template_user_merge_vars = [
            {"name": "USER_NAME", "content": fullname},
            {"name": "EMAIL", "content": email},
            {"name": "PHONE", "content": phone},
            {"name": "TROTTER_ADMIN", "content": recipient_name}
        ]
        self.__send_template__(template_name, sender_email , sender_name, recipient_email, recipient_name, subject, template_user_merge_vars)

    # send email using mandrill template
    def __send_template__(self, template_name, sender_email , sender_name, recipient_email, recipient_name, subject, template_user_merge_vars):
        try:

            # TODO: what is template_content for?
            template_content = [{}]
            message = {
                'from_email': sender_email,
                'from_name': sender_name,
                "merge_vars": [
                    {
                        "rcpt": recipient_email,
                        "vars": template_user_merge_vars
                    }
                ],
                'subject': subject,
                'text': 'Example text content',
                'to': [
                    {
                        'email': recipient_email,
                        'name': recipient_name,
                        'type': 'to'
                    }
                ]
            }
            result = self.__mandrill_client__.messages.send_template(template_name=template_name, template_content=template_content, message=message, async=False, ip_pool='Main Pool')

            print "result"
            print result

        except mandrill.Error, e:
            # Mandrill errors are thrown as exceptions
            print 'A mandrill error occurred: %s - %s' % (e.__class__, e)
            # A mandrill error occurred: <class 'mandrill.UnknownSubaccountError'> - No subaccount exists with the id 'customer-123'
            raise