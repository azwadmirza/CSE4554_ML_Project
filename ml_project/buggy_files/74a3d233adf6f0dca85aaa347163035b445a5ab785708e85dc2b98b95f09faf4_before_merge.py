    def authenticate(self):
        data = self._api_call("authenticate", {"auth": self.auth}, schema=_login_schema)
        self.auth = data["auth"]
        self.cache.set("auth", data["auth"], expires_at=data["expires"])
        return data