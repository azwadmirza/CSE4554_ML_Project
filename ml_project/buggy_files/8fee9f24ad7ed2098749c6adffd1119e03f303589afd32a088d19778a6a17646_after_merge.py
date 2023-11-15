    def reap_monthly_active_users(self):
        """Cleans out monthly active user table to ensure that no stale
        entries exist.

        Returns:
            Deferred[]
        """

        def _reap_users(txn, reserved_users):
            """
            Args:
                reserved_users (tuple): reserved users to preserve
            """

            thirty_days_ago = int(self._clock.time_msec()) - (1000 * 60 * 60 * 24 * 30)
            query_args = [thirty_days_ago]
            base_sql = "DELETE FROM monthly_active_users WHERE timestamp < ?"

            # Need if/else since 'AND user_id NOT IN ({})' fails on Postgres
            # when len(reserved_users) == 0. Works fine on sqlite.
            if len(reserved_users) > 0:
                # questionmarks is a hack to overcome sqlite not supporting
                # tuples in 'WHERE IN %s'
                question_marks = ",".join("?" * len(reserved_users))

                query_args.extend(reserved_users)
                sql = base_sql + " AND user_id NOT IN ({})".format(question_marks)
            else:
                sql = base_sql

            txn.execute(sql, query_args)

            max_mau_value = self.hs.config.max_mau_value
            if self.hs.config.limit_usage_by_mau:
                # If MAU user count still exceeds the MAU threshold, then delete on
                # a least recently active basis.
                # Note it is not possible to write this query using OFFSET due to
                # incompatibilities in how sqlite and postgres support the feature.
                # sqlite requires 'LIMIT -1 OFFSET ?', the LIMIT must be present
                # While Postgres does not require 'LIMIT', but also does not support
                # negative LIMIT values. So there is no way to write it that both can
                # support
                if len(reserved_users) == 0:
                    sql = """
                        DELETE FROM monthly_active_users
                        WHERE user_id NOT IN (
                            SELECT user_id FROM monthly_active_users
                            ORDER BY timestamp DESC
                            LIMIT ?
                        )
                        """
                    txn.execute(sql, (max_mau_value,))
                # Need if/else since 'AND user_id NOT IN ({})' fails on Postgres
                # when len(reserved_users) == 0. Works fine on sqlite.
                else:
                    # Must be >= 0 for postgres
                    num_of_non_reserved_users_to_remove = max(
                        max_mau_value - len(reserved_users), 0
                    )

                    # It is important to filter reserved users twice to guard
                    # against the case where the reserved user is present in the
                    # SELECT, meaning that a legitmate mau is deleted.
                    sql = """
                        DELETE FROM monthly_active_users
                        WHERE user_id NOT IN (
                            SELECT user_id FROM monthly_active_users
                            WHERE user_id NOT IN ({})
                            ORDER BY timestamp DESC
                            LIMIT ?
                        )
                        AND user_id NOT IN ({})
                    """.format(
                        question_marks, question_marks
                    )

                    query_args = [
                        *reserved_users,
                        num_of_non_reserved_users_to_remove,
                        *reserved_users,
                    ]

                    txn.execute(sql, query_args)

            # It seems poor to invalidate the whole cache, Postgres supports
            # 'Returning' which would allow me to invalidate only the
            # specific users, but sqlite has no way to do this and instead
            # I would need to SELECT and the DELETE which without locking
            # is racy.
            # Have resolved to invalidate the whole cache for now and do
            # something about it if and when the perf becomes significant
            self._invalidate_all_cache_and_stream(
                txn, self.user_last_seen_monthly_active
            )
            self._invalidate_cache_and_stream(txn, self.get_monthly_active_count, ())

        reserved_users = yield self.get_registered_reserved_users()
        yield self.db.runInteraction(
            "reap_monthly_active_users", _reap_users, reserved_users
        )