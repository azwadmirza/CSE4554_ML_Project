    def add_cookies_from_ui(self):
        """
        Add the cookies configured from UI to the providers requests session.

        :return: A dict with the the keys result as bool and message as string
        """
        # This is the generic attribute used to manually add cookies for provider authentication
        if self.enable_cookies:
            if self.cookies:
                cookie_validator = re.compile(r'^(\w+=\w+)(;\w+=\w+)*$')
                if not cookie_validator.match(self.cookies):
                    ui.notifications.message(
                        'Failed to validate cookie for provider {provider}'.format(provider=self.name),
                        'Cookie is not correctly formatted: {0}'.format(self.cookies))
                    return {'result': False,
                            'message': 'Cookie is not correctly formatted: {0}'.format(self.cookies)}

                # cookie_validator got at least one cookie key/value pair, let's return success
                add_dict_to_cookiejar(self.session.cookies, dict(x.rsplit('=', 1) for x in self.cookies.split(';')))
                return {'result': True,
                        'message': ''}

            else:  # Cookies not set. Don't need to check cookies
                return {'result': True,
                        'message': 'No Cookies added from ui for provider: {0}'.format(self.name)}

        return {'result': False,
                'message': 'Adding cookies is not supported for provider: {0}'.format(self.name)}