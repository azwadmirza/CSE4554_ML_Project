    def bySound(self, id, count=30, offset=0, **kwargs) -> dict:
        """Returns a dictionary listing TikToks with a specific sound.

        :param id: The sound id to search by.
                   Note: Can be found in the URL of the sound specific page or with other methods.
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

        while len(response) < count:
            if count < maxCount:
                realCount = count
            else:
                realCount = maxCount
            
            query = {
                "secUid": "",
                "musicID": str(id),
                "count": str(realCount),
                "cursor": str(offset),
                "shareUid": "",
                "language": language,
            }
            api_url = "{}api/music/item_list/?{}&{}".format(
                BASE_URL, self.__add_new_params__(), urlencode(query)
            )
            b = browser(api_url, **kwargs)
            res = self.getData(b, proxy=proxy)

            for t in res.get("itemList", []):
                response.append(t)

            if not res["hasMore"]:
                if self.debug:
                    print("TikTok isn't sending more TikToks beyond this point.")
                return response

            realCount = count - len(response)
            offset = res["cursor"]

        return response[:count]