    def password(self) -> str:
        userinfo = self._uri_reference.userinfo or ""
        return unquote(userinfo.partition(":")[2])