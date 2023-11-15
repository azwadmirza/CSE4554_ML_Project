    def _identity_auth(self):
        for identity_file in self.IDENTITIES:
            if not os.path.isfile(identity_file):
                continue
            logger.debug(
                "Trying to authenticate with identity file %s",
                identity_file)
            try:
                self._pkey_auth(identity_file, password=self.password)
            except Exception as ex:
                logger.debug(
                    "Authentication with identity file %s failed with %s, "
                    "continuing with other identities",
                    identity_file, ex)
                continue
            else:
                logger.debug("Authentication succeeded with identity file %s",
                             identity_file)
                return
        raise AuthenticationError("No authentication methods succeeded")