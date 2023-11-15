    def remove_user(self, group_item, user_id):
        self._remove_user(group_item, user_id)
        try:
            user_set = group_item.users
            for user in user_set:
                if user.id == user_id:
                    user_set.remove(user)
                    break
        except UnpopulatedPropertyError:
            # If we aren't populated, do nothing to the user list
            pass
        logger.info('Removed user (id: {0}) from group (ID: {1})'.format(user_id, group_item.id))