    def userPage(self, userID, secUID, page_size=30, minCursor=0, maxCursor=0, **kwargs) -> dict:
        """Returns a dictionary listing of one page of TikToks given a user's ID and secUID

        :param userID: The userID of the user, which TikTok assigns.
        :param secUID: The secUID of the user, which TikTok assigns.
        :param page_size: The number of posts to return per page.
        :param minCursor: time stamp for the earliest TikTok to retrieve
        :param maxCursor: time stamp for the latest TikTok to retrieve
        :param language: The 2 letter code of the language to return.
                         Note: Doesn't seem to have an affect.
        :param region: The 2 letter region code.
                       Note: Doesn't seem to have an affect.
        :param proxy: The IP address of a proxy to make requests from.
        """
        (
            region,
            language,
            proxy,
            maxCount,
        ) = self.__process_kwargs__(kwargs)

        api_url = "https://m.tiktok.com/api/item_list/?{}&count={}&id={}&type=1&secUid={}" "&minCursor={}&maxCursor={}&sourceType=8&appId=1233&region={}&language={}".format(
            self.__add_new_params__(),
            page_size,
            str(userID),
            str(secUID),
            minCursor,
            maxCursor,
            region,
            language,
        )
        b = browser(api_url, **kwargs)
        return self.getData(b, proxy=proxy)