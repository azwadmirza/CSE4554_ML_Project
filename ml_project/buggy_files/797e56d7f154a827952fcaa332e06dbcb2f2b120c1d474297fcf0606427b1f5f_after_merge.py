    def userLikedbyUsername(self, username, count=30, **kwargs) -> dict:
        """Returns a dictionary listing TikToks a user has liked by username.
           Note: The user's likes must be public

        :param username: The username of the user.
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
        data = self.getUserObject(username, **kwargs)
        return self.userLiked(
            data["id"],
            data["secUid"],
            count=count,
            **kwargs,
        )