    def getHashtagDetails(self, hashtag, **kwargs) -> dict:
        """Returns a hashtag object.

        :param hashtag: The hashtag to search by.
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
        query = {"language": language}
        api_url = "{}node/share/tag/{}?{}&{}".format(
            BASE_URL, quote(hashtag), self.__add_new_params__(), urlencode(query)
        )
        b = browser(api_url, **kwargs)
        return self.getData(b, **kwargs)