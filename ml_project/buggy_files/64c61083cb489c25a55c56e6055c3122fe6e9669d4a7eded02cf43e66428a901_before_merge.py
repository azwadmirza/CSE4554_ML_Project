    def login(self):
        """Login method used for logging in before doing search and torrent downloads."""
        if any(dict_from_cookiejar(self.session.cookies).values()):
            return True

        if 'pass' in dict_from_cookiejar(self.session.cookies):
            return True

        login_html = self.session.get(self.urls['login'])
        with BS4Parser(login_html.text, 'html5lib') as html:
            token = html.find('input', attrs={'name': '_token'}).get('value')

        login_params = {
            '_token': token,
            'email_username': self.username,
            'password': self.password,
            'remember': 1,
            'submit': 'Login',
        }

        response = self.session.post(self.urls['login'], data=login_params)
        if not response or not response.text:
            log.warning('Unable to connect to provider')
            return False

        if 'These credentials do not match our records.' in response.text:
            log.warning('Invalid username or password. Check your settings')
            return False

        return True