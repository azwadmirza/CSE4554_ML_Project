    def _send_dm(self, message=None):

        username = self.consumer_key
        password = self.consumer_secret
        dmdest = app.TWITTER_DMTO
        access_token_key = app.TWITTER_USERNAME
        access_token_secret = app.TWITTER_PASSWORD

        log.debug(u'Sending DM: {0} {1}', dmdest, message)

        api = twitter.Api(username, password, access_token_key, access_token_secret)

        try:
            api.PostDirectMessage(message.encode('utf8')[:139], screen_name=dmdest)
        except Exception as error:
            log.error(u'Error Sending Tweet (DM): {!r}', error)
            return False

        return True