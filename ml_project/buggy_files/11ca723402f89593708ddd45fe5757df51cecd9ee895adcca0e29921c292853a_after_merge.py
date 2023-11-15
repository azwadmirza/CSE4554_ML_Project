    def disbatch(self):
        """
        Disbatch all lowstates to the appropriate clients
        """
        ret = []

        # check clients before going, we want to throw 400 if one is bad
        for low in self.lowstate:
            if not self._verify_client(low):
                return

            # Make sure we have 'token' or 'username'/'password' in each low chunk.
            # Salt will verify the credentials are correct.
            if self.token is not None and "token" not in low:
                low["token"] = self.token

            if not (
                ("token" in low)
                or ("username" in low and "password" in low and "eauth" in low)
            ):
                ret.append("Failed to authenticate")
                break

            # disbatch to the correct handler
            try:
                chunk_ret = yield getattr(self, "_disbatch_{}".format(low["client"]))(
                    low
                )
                ret.append(chunk_ret)
            except (AuthenticationError, AuthorizationError, EauthAuthenticationError):
                ret.append("Failed to authenticate")
                break
            except Exception as ex:  # pylint: disable=broad-except
                ret.append("Unexpected exception while handling request: {}".format(ex))
                log.error("Unexpected exception while handling request:", exc_info=True)

        self.write(self.serialize({"return": ret}))
        self.finish()