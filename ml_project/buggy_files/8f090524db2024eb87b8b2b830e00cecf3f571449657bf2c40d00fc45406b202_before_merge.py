    async def fetch_additional_users(self, user_list):
        """
        Alternative method which only fetches defined users
        :param user_list: a list of the users to fetch and parse
        """
        for user in user_list:
            raw_user = await self.facade.aad.get_user(user)
            id, user = await self._parse_user(raw_user)
            self[id] = user