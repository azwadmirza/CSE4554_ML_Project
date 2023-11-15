    def upsert_monthly_active_user_txn(self, txn, user_id):
        """Updates or inserts monthly active user member

        We consciously do not call is_support_txn from this method because it
        is not possible to cache the response. is_support_txn will be false in
        almost all cases, so it seems reasonable to call it only for
        upsert_monthly_active_user and to call is_support_txn manually
        for cases where upsert_monthly_active_user_txn is called directly,
        like _initialise_reserved_users

        In short, don't call this method with support users. (Support users
        should not appear in the MAU stats).

        Args:
            txn (cursor):
            user_id (str): user to add/update

        Returns:
            bool: True if a new entry was created, False if an
            existing one was updated.
        """

        # Am consciously deciding to lock the table on the basis that is ought
        # never be a big table and alternative approaches (batching multiple
        # upserts into a single txn) introduced a lot of extra complexity.
        # See https://github.com/matrix-org/synapse/issues/3854 for more
        is_insert = self.db.simple_upsert_txn(
            txn,
            table="monthly_active_users",
            keyvalues={"user_id": user_id},
            values={"timestamp": int(self._clock.time_msec())},
        )

        self._invalidate_cache_and_stream(txn, self.get_monthly_active_count, ())
        self._invalidate_cache_and_stream(
            txn, self.user_last_seen_monthly_active, (user_id,)
        )

        return is_insert