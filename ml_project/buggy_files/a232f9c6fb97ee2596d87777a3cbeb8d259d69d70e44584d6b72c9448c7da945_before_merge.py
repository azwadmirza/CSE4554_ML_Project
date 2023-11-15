    def auth(self):
        if self.pkey is not None:
            logger.debug(
                "Proceeding with private key file authentication")
            return self._pkey_auth(password=self.password)
        if self.allow_agent:
            try:
                self.session.agent_auth(self.user)
            except (AgentAuthenticationError, AgentConnectionError, AgentGetIdentityError,
                    AgentListIdentitiesError) as ex:
                logger.debug("Agent auth failed with %s"
                             "continuing with other authentication methods", ex)
            except Exception as ex:
                logger.error("Unknown error during agent authentication - %s", ex)
            else:
                logger.debug("Authentication with SSH Agent succeeded")
                return
        try:
            self._identity_auth()
        except AuthenticationException:
            if self.password is None:
                raise
            logger.debug("Private key auth failed, trying password")
            self._password_auth()