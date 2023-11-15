    def discoverHashtags(self, **kwargs) -> dict:
        """Discover page, consists challenges (hashtags)

        :param proxy: The IP address of a proxy server.
        """
        (
            region,
            language,
            proxy,
            maxCount,
        ) = self.__process_kwargs__(kwargs)
        query = {"noUser": 1, "userCount": 30, "scene": 0}
        api_url = "{}node/share/discover?{}&{}".format(
            BASE_URL, self.__add_new_params__(), urlencode(query)
        )
        b = browser(api_url, **kwargs)
        return self.getData(b, proxy=proxy)["body"][1]["exploreList"]