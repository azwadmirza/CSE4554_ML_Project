    def get_user_roles(user=None):
        """
        Get all the roles associated with the user.

        :param user: the ab_user in FAB model.
        :return: a list of roles associated with the user.
        """
        if user is None:
            user = g.user
        if user.is_anonymous:
            public_role = current_app.appbuilder.get_app.config["AUTH_ROLE_PUBLIC"]
            return [current_app.appbuilder.sm.find_role(public_role)] if public_role else []
        return user.roles