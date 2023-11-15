    def set_server_admin(self, user, admin):
        """Sets whether a user is an admin of this homeserver.

        Args:
            user (UserID): user ID of the user to test
            admin (bool): true iff the user is to be a server admin,
                false otherwise.
        """
        return self.db.simple_update_one(
            table="users",
            keyvalues={"name": user.to_string()},
            updatevalues={"admin": 1 if admin else 0},
            desc="set_server_admin",
        )