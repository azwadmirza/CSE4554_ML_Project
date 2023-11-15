    def getUserPager(self, username, page_size=30, minCursor=0, maxCursor=0, **kwargs):
        """Returns a generator to page through a user's feed

        :param username: The username of the user.
        :param page_size: The number of posts to return in a page.
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
        data = self.getUserObject(username, **kwargs)

        while True:
            resp = self.userPage(
                data["id"],
                data["secUid"],
                page_size=page_size,
                maxCursor=maxCursor,
                minCursor=minCursor,
                **kwargs,
            )

            try:
                page = resp["items"]
            except KeyError:
                # No mo results
                return

            maxCursor = resp["maxCursor"]

            yield page

            if not resp["hasMore"]:
                return  # all done