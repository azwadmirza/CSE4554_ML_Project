    def getUser(self, username, **kwargs) -> dict:
        """Gets the full exposed user object

        :param username: The username of the user.
        :param language: The 2 letter code of the language to return.
                         Note: Doesn't seem to have an affect.
        :param proxy: The IP address of a proxy to make requests from.
        """
        (
            region,
            language,
            proxy,
            maxCount,
            did,
        ) = self.__process_kwargs__(kwargs)
        kwargs['custom_did'] = did
        query = {"language": language}
        api_url = "{}node/share/user/@{}?{}&{}".format(
            BASE_URL, quote(username), self.__add_new_params__(), urlencode(query)
        )

        return self.getData(url=api_url, **kwargs)["userInfo"]