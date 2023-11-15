    def userLiked(
        self, userID, secUID, count=30, minCursor=0, maxCursor=0, **kwargs
    ) -> dict:
        """Returns a dictionary listing TikToks that a given a user has liked.
           Note: The user's likes must be public

        :param userID: The userID of the user, which TikTok assigns.
        :param secUID: The secUID of the user, which TikTok assigns.
        :param count: The number of posts to return.
                      Note: seems to only support up to ~2,000
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
        response = []
        first = True

        while len(response) < count:
            if count < maxCount:
                realCount = count
            else:
                realCount = maxCount

            query = {
                "count": realCount,
                "id": userID,
                "type": 2,
                "secUid": secUID,
                "maxCursor": maxCursor,
                "minCursor": minCursor,
                "sourceType": 9,
                "appId": 1233,
                "region": region,
                "priority_region": region,
                "language": language,
            }
            api_url = "{}api/item_list/?{}&{}".format(
                BASE_URL, self.__add_new_params__(), urlencode(query)
            )
            b = browser(api_url, **kwargs)
            res = self.getData(b, **kwargs)

            try:
                res["items"]
            except Exception:
                if self.debug:
                    print("Most Likely User's List is Empty")
                return []

            if "items" in res.keys():
                for t in res["items"]:
                    response.append(t)

            if not res["hasMore"] and not first:
                print("TikTok isn't sending more TikToks beyond this point.")
                return response

            realCount = count - len(response)
            maxCursor = res["maxCursor"]

            first = False

        return response[:count]