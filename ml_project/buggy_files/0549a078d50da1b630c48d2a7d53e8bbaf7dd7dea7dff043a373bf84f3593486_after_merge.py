    def getSuggestedUsersbyID(
        self, userId="6745191554350760966", count=30, **kwargs
    ) -> list:
        """Returns suggested users given a different TikTok user.

        :param userId: The id of the user to get suggestions for.
        :param count: The amount of users to return.
        :param proxy: The IP address of a proxy to make requests from.
        """
        (
            region,
            language,
            proxy,
            maxCount,
        ) = self.__process_kwargs__(kwargs)
        query = {
            "noUser": 0,
            "pageId": userId,
            "userId": userId,
            "userCount": count,
            "scene": 15,
        }
        api_url = "{}node/share/discover?{}&{}".format(
            BASE_URL, self.__add_new_params__(), urlencode(query)
        )
        b = browser(api_url, **kwargs)

        res = []
        for x in self.getData(b, **kwargs)["body"][0]["exploreList"]:
            res.append(x["cardItem"])
        return res[:count]