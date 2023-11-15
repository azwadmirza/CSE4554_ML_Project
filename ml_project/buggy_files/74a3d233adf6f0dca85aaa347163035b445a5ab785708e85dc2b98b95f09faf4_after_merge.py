    def authenticate(self):
        try:
            data = self._api_call("authenticate", {"auth": self.auth}, schema=_login_schema)
        except CrunchyrollAPIError:
            self.auth = None
            self.cache.set("auth", None, expires_at=0)
            log.warning("Saved credentials have expired")
            return

        log.debug("Credentials expire at: {}".format(data["expires"]))
        self.cache.set("auth", self.auth, expires_at=data["expires"])
        return data