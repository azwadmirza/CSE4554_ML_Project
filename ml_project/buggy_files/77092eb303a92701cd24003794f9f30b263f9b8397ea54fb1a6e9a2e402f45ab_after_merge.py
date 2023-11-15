    def getHashtagDetails(self, hashtag, **kwargs) -> dict:
        """Returns a hashtag object.

        :param hashtag: The hashtag to search by.
        :param language: The 2 letter code of the language to return.
                         Note: Doesn't seem to have an affect.
        :param proxy: The IP address of a proxy to make requests from.
        """
        logging.warning("The getHashtagDetails will be deprecated in a future version. Replace it with getHashtagObject")
        (
            region,
            language,
            proxy,
            maxCount,
            did,
        ) = self.__process_kwargs__(kwargs)
        kwargs['custom_did'] = did
        query = {"lang": language}
        api_url = "{}node/share/tag/{}?{}&{}".format(
            BASE_URL, quote(hashtag), self.__add_new_params__(), urlencode(query)
        )

        return self.getData(url=api_url, **kwargs)