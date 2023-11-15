        def delete_pusher_txn(txn, stream_id):
            self._invalidate_cache_and_stream(  # type: ignore
                txn, self.get_if_user_has_pusher, (user_id,)
            )

            # It is expected that there is exactly one pusher to delete, but
            # if it isn't there (or there are multiple) delete them all.
            self.db_pool.simple_delete_txn(
                txn,
                "pushers",
                {"app_id": app_id, "pushkey": pushkey, "user_name": user_id},
            )

            # it's possible for us to end up with duplicate rows for
            # (app_id, pushkey, user_id) at different stream_ids, but that
            # doesn't really matter.
            self.db_pool.simple_insert_txn(
                txn,
                table="deleted_pushers",
                values={
                    "stream_id": stream_id,
                    "app_id": app_id,
                    "pushkey": pushkey,
                    "user_id": user_id,
                },
            )