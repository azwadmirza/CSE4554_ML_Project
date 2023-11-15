    def _create_api(self):
        """Creates a new CrunchyrollAPI object, initiates it's session and
        tries to authenticate it either by using saved credentials or the
        user's username and password.
        """
        if self.options.get("purge_credentials"):
            self.cache.set("session_id", None, 0)
            self.cache.set("auth", None, 0)
            self.cache.set("session_id", None, 0)

        # use the crunchyroll locale as an override, for backwards compatibility
        locale = self.get_option("locale") or self.session.localization.language_code
        api = CrunchyrollAPI(self.cache,
                             self.session,
                             session_id=self.get_option("session_id"),
                             locale=locale)

        if not self.get_option("session_id"):
            self.logger.debug("Creating session with locale: {0}", locale)
            api.start_session()

            if api.auth:
                self.logger.debug("Using saved credentials")
                login = api.authenticate()
                self.logger.info("Successfully logged in as '{0}'",
                                 login["user"]["username"] or login["user"]["email"])
            elif self.options.get("username"):
                try:
                    self.logger.debug("Attempting to login using username and password")
                    api.login(self.options.get("username"),
                              self.options.get("password"))
                    login = api.authenticate()
                    self.logger.info("Logged in as '{0}'",
                                     login["user"]["username"] or login["user"]["email"])

                except CrunchyrollAPIError as err:
                    raise PluginError(u"Authentication error: {0}".format(err.msg))
            else:
                self.logger.warning(
                    "No authentication provided, you won't be able to access "
                    "premium restricted content"
                )

        return api