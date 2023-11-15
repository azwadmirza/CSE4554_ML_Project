    def copy_with(self, **kwargs: typing.Any) -> "URL":
        if (
            "username" in kwargs
            or "password" in kwargs
            or "host" in kwargs
            or "port" in kwargs
        ):
            host = kwargs.pop("host", self.host)
            port = kwargs.pop("port", self.port)
            username = kwargs.pop("username", self.username)
            password = kwargs.pop("password", self.password)

            authority = host
            if port is not None:
                authority += f":{port}"
            if username:
                userpass = username
                if password:
                    userpass += f":{password}"
                authority = f"{userpass}@{authority}"

            kwargs["authority"] = authority

        return URL(self._uri_reference.copy_with(**kwargs).unsplit())