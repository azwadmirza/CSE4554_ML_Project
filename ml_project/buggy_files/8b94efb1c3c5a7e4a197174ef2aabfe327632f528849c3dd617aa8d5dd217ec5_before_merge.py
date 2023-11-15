    def discover_type(self, search_term, prefix, count=28, **kwargs) -> list:
        """Returns a list of whatever the prefix type you pass in

        :param search_term: The string to search by.
        :param prefix: The type of post to search by user/music/challenge.
        :param count: The number of posts to return.
        :param proxy: The IP address of a proxy to make requests from.
        """
        (
            region,
            language,
            proxy,
            maxCount,
        ) = self.__process_kwargs__(kwargs)

        response = []
        offsetCount = 0
        while len(response) < count:
            query = {
                "discoverType": count,
                "needItemList": False,
                "keyWord": search_term,
                "offset": offsetCount,
                "count": 99,
                "useRecommend": False,
                "language": "en",
            }
            api_url = "{}api/discover/{}/?{}&{}".format(
                BASE_URL, prefix, self.__add_new_params__(), urlencode(query)
            )
            b = browser(api_url, **kwargs)
            data = self.getData(b, proxy=proxy)

            if "userInfoList" in data.keys():
                for x in data["userInfoList"]:
                    response.append(x)
            elif "musicInfoList" in data.keys():
                for x in data["musicInfoList"]:
                    response.append(x)
            elif "challengeInfoList" in data.keys():
                for x in data["challengeInfoList"]:
                    response.append(x)
            else:
                if self.debug:
                    print("Nomore results being returned")
                break

            offsetCount = len(response)

        return response[:count]