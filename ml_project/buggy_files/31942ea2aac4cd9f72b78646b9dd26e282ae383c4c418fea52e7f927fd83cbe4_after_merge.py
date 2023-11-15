    def set_server_admin(self, user, admin):
        """Sets whether a user is an admin of this homeserver.

        Args:
            user (UserID): user ID of the user to test
            admin (bool): true iff the user is to be a server admin,
                false otherwise.
        """

        def set_server_admin_txn(txn):
            self.db.simple_update_one_txn(
                txn, "users", {"name": user.to_string()}, {"admin": 1 if admin else 0}
            )
            self._invalidate_cache_and_stream(
                txn, self.get_user_by_id, (user.to_string(),)
            )

        return self.db.runInteraction("set_server_admin", set_server_admin_txn)