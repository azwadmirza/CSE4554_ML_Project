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
        ) = self.__process_kwargs__(kwargs)
        query = {"uniqueId": username, "language": language}
        api_url = "{}api/user/detail/?{}&{}".format(
            BASE_URL, self.__add_new_params__(), urlencode(query)
        )
        b = browser(api_url, **kwargs)
        return self.getData(b, **kwargs)["userInfo"]