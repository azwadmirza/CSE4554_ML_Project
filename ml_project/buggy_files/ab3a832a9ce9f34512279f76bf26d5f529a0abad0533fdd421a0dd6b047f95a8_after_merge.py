    def _login(self, username=None, store_password=False,
               reenter_password=False):
        """
        Login to the ESO User Portal.

        Parameters
        ----------
        username : str, optional
            Username to the ESO Public Portal. If not given, it should be
            specified in the config file.
        store_password : bool, optional
            Stores the password securely in your keyring. Default is False.
        reenter_password : bool, optional
            Asks for the password even if it is already stored in the
            keyring. This is the way to overwrite an already stored passwork
            on the keyring. Default is False.
        """
        if username is None:
            if self.USERNAME == "":
                raise LoginError("If you do not pass a username to login(), "
                                 "you should configure a default one!")
            else:
                username = self.USERNAME

        # Get password from keyring or prompt
        password_from_keyring = None
        if reenter_password is False:
            try:
                password_from_keyring = keyring.get_password(
                    "astroquery:www.eso.org", username)
            except keyring.errors.KeyringError as exc:
                log.warning("Failed to get a valid keyring for password "
                            "storage: {}".format(exc))

        if password_from_keyring is None:
            if system_tools.in_ipynb():
                log.warning("You may be using an ipython notebook:"
                            " the password form will appear in your terminal.")
            password = getpass.getpass("{0}, enter your ESO password:\n"
                                       .format(username))
        else:
            password = password_from_keyring
        # Authenticate
        log.info("Authenticating {0} on www.eso.org...".format(username))

        # Do not cache pieces of the login process
        login_response = self._request("GET", "https://www.eso.org/sso/login",
                                       cache=False)
        root = BeautifulSoup(login_response.content, 'html5lib')
        login_input = root.find(name='input', attrs={'name': 'execution'})
        if login_input is None:
            raise ValueError("ESO login page did not have the correct attributes.")
        execution = login_input.get('value')

        login_result_response = self._request("POST", "https://www.eso.org/sso/login",
                                              data={'username': username,
                                                    'password': password,
                                                    'execution': execution,
                                                    '_eventId': 'submit',
                                                    'geolocation': '',
                                                    })
        login_result_response.raise_for_status()
        root = BeautifulSoup(login_result_response.content, 'html5lib')
        authenticated = root.find('h4').text == 'Login successful'

        if authenticated:
            log.info("Authentication successful!")
        else:
            log.exception("Authentication failed!")

        # When authenticated, save password in keyring if needed
        if authenticated and password_from_keyring is None and store_password:
            keyring.set_password("astroquery:www.eso.org", username, password)
        return authenticated