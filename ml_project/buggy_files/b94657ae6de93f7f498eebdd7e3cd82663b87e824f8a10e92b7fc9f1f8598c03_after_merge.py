    def _sendFreeMobileSMS(self, title, msg, cust_id=None, apiKey=None):
        """
        Send a SMS notification

        msg: The message to send (unicode)
        title: The title of the message
        userKey: The pushover user id to send the message to (or to subscribe with)

        return: True if the message succeeded, False otherwise
        """
        if cust_id is None:
            cust_id = app.FREEMOBILE_ID
        if apiKey is None:
            apiKey = app.FREEMOBILE_APIKEY

        log.debug(u'Free Mobile in use with API KEY: {0}', apiKey)

        # build up the URL and parameters
        msg = '{0}: {1}'.format(title, msg.strip())
        msg_quoted = quote(msg.encode('utf-8'))
        URL = 'https://smsapi.free-mobile.fr/sendmsg?user={user}&pass={api_key}&msg={msg}'.format(
            user=cust_id,
            api_key=apiKey,
            msg=msg_quoted,
        )

        req = Request(URL)
        # send the request to Free Mobile
        try:
            urlopen(req)
        except IOError as e:
            if hasattr(e, 'code'):
                error_message = {
                    400: 'Missing parameter(s).',
                    402: 'Too much SMS sent in a short time.',
                    403: 'API service is not enabled in your account or ID / API key is incorrect.',
                    500: 'Server error. Please retry in few moment.',
                }
                message = error_message.get(e.code)
                if message:
                    log.error(message)
                    return False, message
        except Exception as e:
            message = u'Error while sending SMS: {0}'.format(e)
            log.error(message)
            return False, message

        message = 'Free Mobile SMS successful.'
        log.info(message)
        return True, message