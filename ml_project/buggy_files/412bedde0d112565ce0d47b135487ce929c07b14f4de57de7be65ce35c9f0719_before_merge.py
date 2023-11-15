    def copy_with(self, **kwargs: typing.Any) -> "URL":
        """
        Copy this URL, returning a new URL with some components altered.
        Accepts the same set of parameters as the components that are made
        available via properties on the `URL` class.

        For example:

        url = httpx.URL("https://www.example.com").copy_with(username="jo@gmail.com", password="a secret")
        assert url == "https://jo%40email.com:a%20secret@www.example.com"
        """
        allowed = {
            "scheme": str,
            "username": str,
            "password": str,
            "userinfo": bytes,
            "host": str,
            "port": int,
            "netloc": str,
            "path": str,
            "query": bytes,
            "raw_path": bytes,
            "fragment": str,
        }
        for key, value in kwargs.items():
            if key not in allowed:
                message = f"{key!r} is an invalid keyword argument for copy_with()"
                raise TypeError(message)
            if value is not None and not isinstance(value, allowed[key]):
                expected = allowed[key].__name__
                seen = type(value).__name__
                message = f"Argument {key!r} must be {expected} but got {seen}"
                raise TypeError(message)

        # Replace username, password, userinfo, host, port, netloc with "authority" for rfc3986
        if "username" in kwargs or "password" in kwargs:
            # Consolidate username and password into userinfo.
            username = quote(kwargs.pop("username", self.username) or "")
            password = quote(kwargs.pop("password", self.password) or "")
            userinfo = f"{username}:{password}" if password else username
            kwargs["userinfo"] = userinfo.encode("ascii")

        if "host" in kwargs or "port" in kwargs:
            # Consolidate host and port into  netloc.
            host = kwargs.pop("host", self.host) or ""
            port = kwargs.pop("port", self.port)
            kwargs["netloc"] = f"{host}:{port}" if port is not None else host

        if "userinfo" in kwargs or "netloc" in kwargs:
            # Consolidate userinfo and netloc into authority.
            userinfo = (kwargs.pop("userinfo", self.userinfo) or b"").decode("ascii")
            netloc = kwargs.pop("netloc", self.netloc) or ""
            authority = f"{userinfo}@{netloc}" if userinfo else netloc
            kwargs["authority"] = authority

        if "raw_path" in kwargs:
            raw_path = kwargs.pop("raw_path") or b""
            path, has_query, query = raw_path.decode("ascii").partition("?")
            kwargs["path"] = path
            kwargs["query"] = query if has_query else None

        else:
            # Ensure path=<url quoted str> for rfc3986
            if kwargs.get("path") is not None:
                kwargs["path"] = quote(kwargs["path"])

            # Ensure query=<str> for rfc3986
            if kwargs.get("query") is not None:
                kwargs["query"] = kwargs["query"].decode("ascii")

        return URL(self._uri_reference.copy_with(**kwargs).unsplit())