    def trending(self, count=30, language='en', region='US', proxy=None) -> dict:
        """
          Gets trending TikToks
        """
        response = []
        maxCount = 50
        maxCursor = 0
        first = True

        while len(response) < count:
            if count < maxCount:
                realCount = count
            else:
                realCount = maxCount

            query = {
                'count': realCount,
                'id': 1,
                'type': 5,
                'secUid': '',
                'maxCursor': maxCursor,
                'minCursor': 0,
                'sourceType': 12,
                'appId': 1233,
                'region': region,
                'language': language
            }
            api_url = "{}api/item_list/?{}&{}".format(
                BASE_URL, self.__add_new_params__(), urlencode(query)
            )
            b = browser(api_url, language=language, proxy=proxy)
            res = self.getData(b, proxy=proxy)

            if 'items' in res.keys():
                for t in res['items']:
                    response.append(t)

            if not res['hasMore'] and not first:
                if self.debug:
                    print("TikTok isn't sending more TikToks beyond this point.")
                return response

            realCount = count - len(response)
            maxCursor = res['maxCursor']

            first = False

        return response[:count]