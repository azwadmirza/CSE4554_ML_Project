    def getMusicObject(self, id, **kwargs) -> dict:
        """Returns a music object for a specific sound id.

        :param id: The sound id to search by.
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

        query = {"musicId": id, "language": language}
        api_url = "{}api/music/detail/?{}&{}".format(
            BASE_URL, self.__add_new_params__(), urlencode(query)
        )

        return self.getData(url=api_url, **kwargs)