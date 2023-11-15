    def auth(self):
        if self.pkey is not None:
            logger.debug(
                "Proceeding with private key file authentication")
            return self._pkey_auth(self.pkey, password=self.password)
        if self.allow_agent:
            try:
                self._agent_auth()
            except (AgentAuthenticationError, AgentConnectionError, AgentGetIdentityError,
                    AgentListIdentitiesError) as ex:
                logger.debug("Agent auth failed with %s"
                             "continuing with other authentication methods", ex)
            except Exception as ex:
                logger.error("Agent auth failed with - %s", ex)
            else:
                logger.debug("Authentication with SSH Agent succeeded")
                return
        if self.identity_auth:
            try:
                return self._identity_auth()
            except AuthenticationError:
                if self.password is None:
                    raise
        logger.debug("Private key auth failed, trying password")
        self._password_auth()