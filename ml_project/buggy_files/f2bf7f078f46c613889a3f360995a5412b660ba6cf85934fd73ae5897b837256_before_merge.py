    def auth(self):
        if self.pkey is not None:
            logger.debug(
                "Proceeding with private key file authentication")
            return self._pkey_auth(self.pkey, password=self.password)
        if self.allow_agent:
            try:
                self.session.userauth_agent(self.user)
            except Exception as ex:
                logger.debug(
                    "Agent auth failed with %s, "
                    "continuing with other authentication methods",
                    ex)
            else:
                logger.debug(
                    "Authentication with SSH Agent succeeded.")
                return
        if self.gssapi_auth or (self.gssapi_server_identity or self.gssapi_client_identity):
            try:
                self.session.userauth_gssapi()
            except Exception as ex:
                logger.error(
                    "GSSAPI authentication with server id %s and client id %s failed - %s",
                    self.gssapi_server_identity, self.gssapi_client_identity,
                    ex)
        if self.identity_auth:
            try:
                self._identity_auth()
            except AuthenticationError:
                if self.password is None:
                    raise
        logger.debug("Private key auth failed, trying password")
        self._password_auth()