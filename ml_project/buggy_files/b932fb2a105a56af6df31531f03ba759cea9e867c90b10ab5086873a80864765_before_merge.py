    def username(self) -> str:
        userinfo = self._uri_reference.userinfo or ""
        return userinfo.partition(":")[0]