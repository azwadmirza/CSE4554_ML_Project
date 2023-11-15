    def cookie_login(self, check_login_text, check_url=None):
        """
        Check the response for text that indicates a login prompt.

        In that case, the cookie authentication was not successful.
        :param check_login_text: A string that's visible when the authentication failed.
        :param check_url: The url to use to test the login with cookies. By default the providers home page is used.

        :return: False when authentication was not successful. True if successful.
        """
        check_url = check_url or self.url

        if self.check_required_cookies():
            # All required cookies have been found within the current session, we don't need to go through this again.
            return True

        if self.cookies:
            result = self.add_cookies_from_ui()
            if not result['result']:
                ui.notifications.message(result['message'])
                log.warning(result['message'])
                return False
        else:
            log.warning('Failed to login, you will need to add your cookies in the provider settings')
            ui.notifications.error('Failed to auth with {provider}'.format(provider=self.name),
                                   'You will need to add your cookies in the provider settings')
            return False

        response = self.session.get(check_url)
        if not response or any([not (response.text and response.status_code == 200),
                                check_login_text.lower() in response.text.lower()]):
            log.warning('Please configure the required cookies for this provider. Check your provider settings')
            ui.notifications.error('Wrong cookies for {provider}'.format(provider=self.name),
                                   'Check your provider settings')
            self.session.cookies.clear()
            return False
        else:
            return True