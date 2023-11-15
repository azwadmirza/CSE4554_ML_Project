    def _store_room_members_txn(self, txn, events, backfilled):
        """Store a room member in the database.
        """

        def str_or_none(val: Any) -> Optional[str]:
            return val if isinstance(val, str) else None

        self.db_pool.simple_insert_many_txn(
            txn,
            table="room_memberships",
            values=[
                {
                    "event_id": event.event_id,
                    "user_id": event.state_key,
                    "sender": event.user_id,
                    "room_id": event.room_id,
                    "membership": event.membership,
                    "display_name": str_or_none(event.content.get("displayname")),
                    "avatar_url": str_or_none(event.content.get("avatar_url")),
                }
                for event in events
            ],
        )

        for event in events:
            txn.call_after(
                self.store._membership_stream_cache.entity_has_changed,
                event.state_key,
                event.internal_metadata.stream_ordering,
            )
            txn.call_after(
                self.store.get_invited_rooms_for_local_user.invalidate,
                (event.state_key,),
            )

            # We update the local_current_membership table only if the event is
            # "current", i.e., its something that has just happened.
            #
            # This will usually get updated by the `current_state_events` handling,
            # unless its an outlier, and an outlier is only "current" if it's an "out of
            # band membership", like a remote invite or a rejection of a remote invite.
            if (
                self.is_mine_id(event.state_key)
                and not backfilled
                and event.internal_metadata.is_outlier()
                and event.internal_metadata.is_out_of_band_membership()
            ):
                self.db_pool.simple_upsert_txn(
                    txn,
                    table="local_current_membership",
                    keyvalues={"room_id": event.room_id, "user_id": event.state_key},
                    values={
                        "event_id": event.event_id,
                        "membership": event.membership,
                    },
                )