    def _send_telegram_msg(self, title, msg, user_id=None, api_key=None):
        """
        Sends a Telegram notification

        :param title: The title of the notification to send
        :param msg: The message string to send
        :param id: The Telegram user/group id to send the message to
        :param api_key: Your Telegram bot API token

        :returns: True if the message succeeded, False otherwise
        """
        user_id = app.TELEGRAM_ID if user_id is None else user_id
        api_key = app.TELEGRAM_APIKEY if api_key is None else api_key

        log.debug('Telegram in use with API KEY: {0}', api_key)

        message = '{0} : {1}'.format(title, msg).encode('utf-8')
        payload = {'chat_id': user_id, 'text': message}
        telegram_api = 'https://api.telegram.org/bot{api_key}/sendMessage'

        success = False
        try:
            r = requests.post(telegram_api.format(api_key=api_key), data=payload)
            r.raise_for_status()
            message = 'Telegram message sent successfully.'
            success = True
        except RequestException as error:
            message = 'Unknown IO error: %s' % error
            if hasattr(error, 'response'):
                error_message = {
                    400: 'Missing parameter(s). Double check your settings or if the channel/user exists.',
                    401: 'Authentication failed.',
                    420: 'Too many messages.',
                    500: 'Server error. Please retry in a few moments.',
                }
                if error.response.status_code in error_message:
                    message = error_message.get(error.response.status_code)
                else:
                    message = http_status_code.get(error.response.status_code, message)
        except Exception as e:
            message = 'Error while sending Telegram message: %s ' % e
        finally:
            log.info(message)
        return success, message