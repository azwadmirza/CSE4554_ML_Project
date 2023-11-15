    def login(self):
        """Login method used for logging in before doing search and torrent downloads."""
        if dict_from_cookiejar(self.session.cookies).get('uid') and \
                dict_from_cookiejar(self.session.cookies).get('pass'):
            return True

        if self.cookies:
            self.add_cookies_from_ui()
        else:
            logger.log('Failed to login, you must add your cookies in the provider settings', logger.WARNING)
            return False

        login_params = {
            'username': self.username,
            'password': self.password,
            'submit.x': 0,
            'submit.y': 0,
        }

        response = self.get_url(self.urls['login'], post_data=login_params, returns='response')
        if not response or not (response.content and response.status_code == 200):
            logger.log('Unable to connect to provider', logger.WARNING)
            return False

        if re.search('You tried too often', response.text):
            logger.log('Too many login access attempts', logger.WARNING)
            return False

        if (dict_from_cookiejar(self.session.cookies).get('uid') and
                dict_from_cookiejar(self.session.cookies).get('uid') in response.text):
            return True
        else:
            logger.log('Failed to login, check your cookies', logger.WARNING)
            self.session.cookies.clear()
            return False