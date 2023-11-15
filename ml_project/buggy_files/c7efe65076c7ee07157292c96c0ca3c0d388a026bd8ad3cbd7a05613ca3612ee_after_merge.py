    def add_user(self, group_item, user_id):
        new_user = self._add_user(group_item, user_id)
        try:
            users = group_item.users
            users.append(new_user)
            group_item._set_users(users)
        except UnpopulatedPropertyError:
            # If we aren't populated, do nothing to the user list
            pass
        logger.info('Added user (id: {0}) to group (ID: {1})'.format(user_id, group_item.id))