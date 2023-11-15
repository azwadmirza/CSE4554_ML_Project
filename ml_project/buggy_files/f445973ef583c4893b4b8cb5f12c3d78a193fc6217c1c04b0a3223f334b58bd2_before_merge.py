    async def fetch_additional_users(self, user_list):
        """
        Special method to fetch additional users
        """
        # fetch the users
        additional_users = Users(self.facade)
        await additional_users.fetch_additional_users(user_list)
        # add them to the resource and update count
        self['users'].update(additional_users)
        self['users_count'] = len(self['users'].values())
        # re-run the finalize method
        await self.finalize()