    def remove_user(self, group_item, user_id):
        self._remove_user(group_item, user_id)
        try:
            users = group_item.users
            for user in users:
                if user.id == user_id:
                    users.remove(user)
                    break
        except UnpopulatedPropertyError:
            # If we aren't populated, do nothing to the user list
            pass
        logger.info('Removed user (id: {0}) from group (ID: {1})'.format(user_id, group_item.id))