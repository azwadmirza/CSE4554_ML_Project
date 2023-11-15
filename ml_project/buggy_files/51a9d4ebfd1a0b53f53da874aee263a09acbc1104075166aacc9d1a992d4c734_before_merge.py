    def trending(self, count=30, minCursor=0, maxCursor=0, **kwargs) -> dict:
        """
        Gets trending TikToks
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
                "id": 1,
                "secUid": "",
                "maxCursor": maxCursor,
                "minCursor": minCursor,
                "sourceType": 12,
                "appId": 1233,
                "region": region,
                "priority_region": region,
                "language": language,
            }
            api_url = "{}api/item_list/?{}&{}".format(
                BASE_URL, self.__add_new_params__(), urlencode(query)
            )
            b = browser(api_url, **kwargs)
            res = self.getData(b, proxy=proxy)

            for t in res.get("items", []):
                response.append(t)

            if not res["hasMore"] and not first:
                if self.debug:
                    print("TikTok isn't sending more TikToks beyond this point.")
                return response[:count]

            realCount = count - len(response)
            maxCursor = res["maxCursor"]

            first = False

        return response[:count]